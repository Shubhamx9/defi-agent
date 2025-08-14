from fastapi import APIRouter
from pydantic import BaseModel
from backend.ai.chains.intent_chain import classify_intent
from backend.ai.chains.query_chain import run_query_chain
from backend.ai.chains.action_extraction_chain import extract_action_details
import json
from backend.utils.cache import get_cached_response, set_cached_response
import uuid

router = APIRouter()

class UserQuery(BaseModel):
    query: str
    session_id: str = None

SESSION_TTL = 3600  # 1 hour

def merge_action_details(old: dict, new: dict) -> dict:
    """Merge new action details into old, preferring new values if present."""
    merged = old.copy()
    for k, v in new.items():
        if v is not None:
            merged[k] = v
    return merged

@router.post("/start-session")
def start_session():
    """Start a new session and return a unique session_id."""
    session_id = str(uuid.uuid4())
    return {"session_id": session_id}

@router.post("/")
def handle_query(user_input: UserQuery):
    q = user_input.query.strip()
    if not q:
        return {"error": "Empty query"}

    session_id = user_input.session_id
    intent = classify_intent(q)

    if intent == "action_request":
        details = extract_action_details(q)
        # Use session_id to persist action details
        if session_id:
            cached = get_cached_response(session_id)
            if cached:
                cached_details = json.loads(cached)
                details = merge_action_details(cached_details, details)
            set_cached_response(session_id, json.dumps(details), ttl=SESSION_TTL)
        return {
            "intent": intent,
            "intent_confidence": None,
            "action_details": details,
            "next_step": "fetch_apy_and_confirm",
            "session_id": session_id
        }

    if intent == "general_query":
        result = run_query_chain(q)
        return {"intent": intent, **result, "session_id": session_id}

    # clarification or unknown → keep it simple: use the same low-cost fallback
    result = run_query_chain(q)  # this already asks a clarifying Q if needed
    return {"intent": "clarification", **result, "session_id": session_id}
