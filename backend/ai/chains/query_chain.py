# backend/ai/chains/query_chain.py
from typing import Any, Dict
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from backend.utils.embedding import get_embedding
from backend.utils.vector_db import query_vector_db
from backend.utils.cache import get_cached_response, set_cached_response
import json
import time

# LLM for refinement / fallback
_mini = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ---------- Session Helpers (Redis) ----------
SESSION_TTL = 300  # seconds

def _get_session_key(user_id: str) -> str:
    return f"session:{user_id}"

def get_user_session(user_id: str) -> Dict:
    raw = get_cached_response(_get_session_key(user_id))
    return json.loads(raw) if raw else {}

def update_user_session(user_id: str, data: Dict):
    set_cached_response(_get_session_key(user_id), json.dumps(data), ttl=SESSION_TTL)

# ---------- Internal Helpers ----------
def _best_text(matches) -> str:
    if not matches:
        return ""
    top = matches[0].metadata or {}
    return top.get("response") or top.get("text") or ""

# ---------- Main Query Chain ----------
def run_query_chain(user_id: str, user_query: str) -> Dict[str, Any]:
    """
    Vector search → scoring thresholds:
      - >= 0.98 → direct DB answer
      - 0.90–0.98 → refine with LLM
      - < 0.90 → LLM fallback
    Also tracks user session for partial info handling.
    """
    # Maintain per-user session
    session_data = get_user_session(user_id)
    session_data["last_query"] = user_query
    session_data["last_updated"] = time.time()
    update_user_session(user_id, session_data)

    emb = get_embedding(user_query)
    matches = query_vector_db(emb, top_k=3)

    # --- No DB hit
    if not matches:
        prompt = f"User asked: {user_query}\nProvide a concise, correct DeFi answer."
        resp = _mini.invoke(prompt)
        return {
            "source": "llm_fallback",
            "confidence": 0.0,
            "answer": resp.content.strip(),
            "top_matches": []
        }

    score = float(matches[0].score or 0.0)

    # --- High confidence
    if score >= 0.98:
        return {
            "source": "vector_db",
            "confidence": score,
            "answer": _best_text(matches),
            "top_matches": [{"score": float(m.score), "metadata": m.metadata} for m in matches]
        }

    # --- Medium confidence
    if score >= 0.90:
        db_texts = [m.metadata.get("response") or m.metadata.get("text") or "" for m in matches if m.metadata]
        context = "\n\n---\n".join([t for t in db_texts if t])
        refine_prompt = ChatPromptTemplate.from_template(
            """Improve and complete the DeFi answer using the database context.
Keep it accurate; do not invent facts. Be concise.

User: {query}
Database context:
{context}

Final improved answer:"""
        )
        refined = _mini.invoke(refine_prompt.format_messages(query=user_query, context=context or "(no context)"))
        return {
            "source": "vector_db + mini_llm",
            "confidence": score,
            "answer": refined.content.strip(),
            "top_matches": [{"score": float(m.score), "metadata": m.metadata} for m in matches]
        }

    # --- Low confidence
    fallback_prompt = ChatPromptTemplate.from_template(
        """The user asked: {query}
Provide a concise, correct DeFi answer. If ambiguous, ask 1 clarifying question."""
    )
    out = _mini.invoke(fallback_prompt.format_messages(query=user_query))
    return {
        "source": "llm_fallback",
        "confidence": score,
        "answer": out.content.strip(),
        "top_matches": [{"score": float(m.score), "metadata": m.metadata} for m in matches]
    }
