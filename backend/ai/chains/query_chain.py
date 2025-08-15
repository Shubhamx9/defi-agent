from typing import Any, Dict, List
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from backend.utils.embedding import get_embedding
from backend.utils.vector_db import query_vector_db
from backend.models.schemas import QueryChainResult, SessionData, VectorMatch
from backend.utils.model_selector import get_query_model
from backend.utils.session_manager import SessionManager
from langsmith import traceable
import json
import time
import logging

logger = logging.getLogger(__name__)

def _get_query_model():
    """Get query processing model with fallback handling."""
    return get_query_model()

# ---------- Session Helpers (Using Session Manager) ----------
def get_user_session(session_id: str) -> SessionData:
    """Get user session data using the session manager."""
    session_data = SessionManager.get_session(session_id)
    if session_data:
        return session_data
    
    # Return default session if not found
    return SessionData(user_id=session_id)

def update_user_session(session_id: str, session_data: SessionData, ip_address: str = None):
    """Update user session using the session manager."""
    SessionManager.update_session(session_id, session_data, ip_address)

# ---------- Internal Helpers ----------
def _convert_matches_to_schema(matches) -> List[VectorMatch]:
    """Convert raw Pinecone matches to schema objects."""
    if not matches:
        return []
    
    schema_matches = []
    for match in matches:
        schema_matches.append(VectorMatch(
            score=float(match.score or 0.0),
            metadata=match.metadata or {}
        ))
    return schema_matches

def _best_text(matches: List[VectorMatch]) -> str:
    """Extract best text from schema-validated matches."""
    if not matches:
        return ""
    top_metadata = matches[0].metadata
    return top_metadata.get("response") or top_metadata.get("text") or ""

@traceable(name="DeFi Query Chain")
def run_query_chain(session_id: str, user_query: str, ip_address: str = None) -> QueryChainResult:
    """
    Cost-efficient conversational query chain with smart context usage:
      - >= 0.98 → direct DB answer (no LLM cost)
      - 0.90–0.98 → refine with LLM + minimal context if needed
      - < 0.90 → LLM fallback + context only for follow-ups
    """
    # Get session data for conversation context
    session_data = get_user_session(session_id)
    
    # Vector search first (always do this - it's cheap)
    emb = get_embedding(user_query)
    raw_matches = query_vector_db(emb, top_k=3)
    matches = _convert_matches_to_schema(raw_matches)

    # Determine if we need conversation context (cost-aware)
    needs_context = session_data.needs_context(user_query)
    conversation_context = session_data.get_smart_context(user_query) if needs_context else ""

    # --- No DB hit - LLM fallback with smart context
    if not matches:
        query_model = _get_query_model()
        if conversation_context:
            prompt = f"""Previous context: {conversation_context}

Current question: {user_query}

Provide a concise, correct DeFi answer considering the context."""
        else:
            prompt = f"User asked: {user_query}\nProvide a concise, correct DeFi answer."
        
        resp = query_model.invoke(prompt)
        answer = resp.content.strip()
        
        # Update session with this exchange
        from backend.models.schemas import IntentType
        session_data.add_turn(user_query, answer, IntentType.GENERAL_QUERY, 0.0, "llm_fallback")
        update_user_session(session_id, session_data, ip_address)
        
        return QueryChainResult(
            source="llm_fallback",
            confidence=0.0,
            answer=answer,
            top_matches=[]
        )

    score = matches[0].score

    # --- High confidence - Direct DB answer (NO LLM COST!)
    if score >= 0.98:
        answer = _best_text(matches)
        
        # Update session with this exchange
        from backend.models.schemas import IntentType
        session_data.add_turn(user_query, answer, IntentType.GENERAL_QUERY, score, "vector_db")
        update_user_session(user_id, session_data)
        
        return QueryChainResult(
            source="vector_db",
            confidence=score,
            answer=answer,
            top_matches=matches
        )

    # --- Medium confidence - Refine with LLM + smart context
    if score >= 0.90:
        db_texts = [m.metadata.get("response") or m.metadata.get("text") or "" 
                   for m in matches if m.metadata]
        db_context = "\n\n---\n".join([t for t in db_texts if t])
        
        # Build prompt with minimal context
        query_model = _get_query_model()
        if conversation_context:
            refine_prompt = ChatPromptTemplate.from_template(
                """Context: {conversation_context}
Question: {query}
Data: {db_context}

Concise DeFi answer:"""
            )
            refined = query_model.invoke(refine_prompt.format_messages(
                query=user_query,
                db_context=db_context or "none",
                conversation_context=conversation_context
            ))
        else:
            refine_prompt = ChatPromptTemplate.from_template(
                """Question: {query}
Data: {db_context}

Concise answer:"""
            )
            refined = query_model.invoke(refine_prompt.format_messages(
                query=user_query, 
                db_context=db_context or "none"
            ))
        
        answer = refined.content.strip()
        
        # Update session with this exchange
        from backend.models.schemas import IntentType
        session_data.add_turn(user_query, answer, IntentType.GENERAL_QUERY, score, "vector_db + mini_llm")
        update_user_session(user_id, session_data)
        
        return QueryChainResult(
            source="vector_db + mini_llm",
            confidence=score,
            answer=answer,
            top_matches=matches
        )

    # --- Low confidence - LLM fallback with smart context
    query_model = _get_query_model()
    if conversation_context:
        fallback_prompt = ChatPromptTemplate.from_template(
            """Context: {conversation_context}
Question: {query}

Concise DeFi answer or clarifying question:"""
        )
        out = query_model.invoke(fallback_prompt.format_messages(
            query=user_query,
            conversation_context=conversation_context
        ))
    else:
        fallback_prompt = ChatPromptTemplate.from_template(
            """Question: {query}
Concise DeFi answer or clarifying question:"""
        )
        out = query_model.invoke(fallback_prompt.format_messages(query=user_query))
    
    answer = out.content.strip()
    
    # Update session with this exchange
    from backend.models.schemas import IntentType
    session_data.add_turn(user_query, answer, IntentType.GENERAL_QUERY, score, "llm_fallback")
    update_user_session(user_id, session_data)
    
    return QueryChainResult(
        source="llm_fallback",
        confidence=score,
        answer=answer,
        top_matches=matches
    )


# Backward compatibility function with IP tracking
def run_query_chain_dict(session_id: str, user_query: str, ip_address: str = None) -> Dict[str, Any]:
    """Backward compatibility wrapper that returns dict instead of schema."""
    result = run_query_chain(session_id, user_query, ip_address)
    return {
        "source": result.source,
        "confidence": result.confidence,
        "answer": result.answer,
        "top_matches": [{"score": m.score, "metadata": m.metadata} for m in result.top_matches],
        "sources": result.sources or []
    }
