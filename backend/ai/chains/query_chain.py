from typing import Any, Dict, List, Optional
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from backend.utils.embedding import get_embedding
from backend.utils.vector_db import query_vector_db
from backend.models.schemas import QueryChainResult, SessionData, VectorMatch
from backend.utils.model_selector import get_query_model
from backend.utils.session_manager import SessionManager
from langsmith import traceable
from backend.logging_setup import logger

def _get_query_model():
    """Get query processing model with fallback handling."""
    return get_query_model()


# ---------- Session Helpers (Using Session Manager) ----------
def get_user_session(
    user_id: str,
    session_id: Optional[str],
    ip_address: str = None,
    user_agent: str = None
) -> tuple[str, SessionData]:
    """
    Always return a valid session for this user.
    - If session exists in Redis → return (same session_id, session_data)
    - If not found → create a new session and return (new_session_id, session_data)
    """
    if session_id:
        session_data = SessionManager.get_session(user_id, session_id)
        if session_data:
            return session_id, session_data

    # Create a new session if missing/invalid
    new_session_id = SessionManager.create_new_session(
        user_id=user_id,
        ip=ip_address or "unknown",
        user_agent=user_agent
    )
    logger.warning(f"Session {session_id} not found, created new session {new_session_id} for user {user_id}")

    new_session_data = SessionManager.get_session(user_id, new_session_id)
    return new_session_id, new_session_data


def update_user_session(user_id: str, session_id: str, session_data: SessionData, ip_address: str = None):
    SessionManager.update_session(session_id, session_data, ip_address)


# ---------- Internal Helpers ----------
def _convert_matches_to_schema(matches) -> List[VectorMatch]:
    if not matches:
        return []
    return [
        VectorMatch(
            score=float(match.score or 0.0),
            metadata=match.metadata or {}
        )
        for match in matches
    ]


def _best_text(matches: List[VectorMatch]) -> str:
    if not matches:
        return ""
    top_metadata = matches[0].metadata
    return top_metadata.get("response") or top_metadata.get("text") or ""


# ---------- Main Query Chain ----------
@traceable(name="DeFi Query Chain")
def run_query_chain(
    user_id: str,
    user_query: str,
    session_id: Optional[str] = None,
    ip_address: str = None,
    user_agent: str = None
) -> QueryChainResult:
    """
    Cost-efficient conversational query chain:
      - >= 0.98 → direct DB answer
      - 0.90–0.98 → refine with LLM
      - < 0.90 → LLM fallback
    Ensures Redis-backed session always exists per user_id.
    """
    # Always resolve session (reuse or create new one)
    session_id, session_data = get_user_session(user_id, session_id, ip_address, user_agent)

    # Vector search first
    emb = get_embedding(user_query)
    raw_matches = query_vector_db(emb, top_k=3)
    matches = _convert_matches_to_schema(raw_matches)

    # Conversation context
    needs_context = session_data.needs_context(user_query)
    conversation_context = session_data.get_smart_context(user_query) if needs_context else ""

    # --- Case 1: No DB hit - LLM fallback
    if not matches:
        query_model = _get_query_model()
        prompt = (
            f"Previous context: {conversation_context}\n\nCurrent question: {user_query}\nProvide a concise DeFi answer."
            if conversation_context else
            f"User asked: {user_query}\nProvide a concise DeFi answer."
        )
        resp = query_model.invoke(prompt)
        answer = resp.content.strip()

        from backend.models.schemas import IntentType
        session_data.add_turn(user_query, answer, IntentType.GENERAL_QUERY, 0.0, "llm_fallback")
        update_user_session(user_id, session_id, session_data, ip_address)

        return QueryChainResult(session_id=session_id, source="llm_fallback", confidence=0.0, answer=answer, top_matches=[])

    score = matches[0].score

    # --- Case 2: High confidence - Direct DB answer
    if score >= 0.98:
        answer = _best_text(matches)
        from backend.models.schemas import IntentType
        session_data.add_turn(user_query, answer, IntentType.GENERAL_QUERY, score, "vector_db")
        update_user_session(user_id, session_id, session_data, ip_address)

        return QueryChainResult(session_id=session_id, source="vector_db", confidence=score, answer=answer, top_matches=matches)

    # --- Case 3: Medium confidence - Refine with LLM
    if score >= 0.90:
        db_texts = [m.metadata.get("response") or m.metadata.get("text") or "" for m in matches if m.metadata]
        db_context = "\n\n---\n".join([t for t in db_texts if t])
        query_model = _get_query_model()

        refine_prompt = ChatPromptTemplate.from_template(
            """{extra}Question: {query}
Data: {db_context}

Concise DeFi answer:"""
        )

        refined = query_model.invoke(refine_prompt.format_messages(
            query=user_query,
            db_context=db_context or "none",
            extra=f"Context: {conversation_context}\n" if conversation_context else ""
        ))

        answer = refined.content.strip()
        from backend.models.schemas import IntentType
        session_data.add_turn(user_query, answer, IntentType.GENERAL_QUERY, score, "vector_db + mini_llm")
        update_user_session(user_id, session_id, session_data, ip_address)

        return QueryChainResult(session_id=session_id, source="vector_db + mini_llm", confidence=score, answer=answer, top_matches=matches)

    # --- Case 4: Low confidence - LLM fallback
    query_model = _get_query_model()
    fallback_prompt = ChatPromptTemplate.from_template(
        """{extra}Question: {query}
Concise DeFi answer or clarifying question:"""
    )

    out = query_model.invoke(fallback_prompt.format_messages(
        query=user_query,
        extra=f"Context: {conversation_context}\n" if conversation_context else ""
    ))

    answer = out.content.strip()
    from backend.models.schemas import IntentType
    session_data.add_turn(user_query, answer, IntentType.GENERAL_QUERY, score, "llm_fallback")
    update_user_session(user_id, session_id, session_data, ip_address)

    return QueryChainResult(session_id=session_id, source="llm_fallback", confidence=score, answer=answer, top_matches=matches)


# ---------- Backward-compatible dict wrapper ----------
def run_query_chain_dict(
    user_id: str,
    user_query: str,
    session_id: Optional[str] = None,
    ip_address: str = None,
    user_agent: str = None
) -> dict:
    result = run_query_chain(user_id, user_query, session_id, ip_address, user_agent)
    return {
        "session_id": result.session_id,
        "source": result.source,
        "confidence": result.confidence,
        "answer": result.answer,
        "top_matches": [m.dict() for m in result.top_matches] if result.top_matches else []
    }
