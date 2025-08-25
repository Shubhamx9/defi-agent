from fastapi import APIRouter, HTTPException, Request, Response
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Optional
from backend.models.schemas import (
    UserQuery,
    QueryResponse,
    ActionDetails,
    IntentType,
    TransactionReadiness
)
from backend.ai.chains.intent_chain import classify_intent
from backend.ai.chains.query_chain import run_query_chain_dict
from backend.ai.chains.action_extraction_chain import extract_action_details_dict
from backend.middleware.input_sanitizer import sanitize_text_input, validate_query_safety
from backend.config.settings import security_settings
from backend.utils.session_manager import SessionManager
from backend.utils.transaction_analyzer import TransactionAnalyzer
from backend.utils.question_generator import QuestionGenerator
from backend.logging_setup import logger

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

# Respect DEBUG for local dev (so cookies work over HTTP in dev)
COOKIE_COMMON = {
    "httponly": True,
    "secure": False if getattr(security_settings, "DEBUG", False) else True,
    "samesite": "lax",         # adjust to 'strict' if needed
    "max_age": 3600,
}

@router.post("/", response_model=QueryResponse)
@limiter.limit(f"{security_settings.RATE_LIMIT_PER_MINUTE}/minute")
def handle_query(
    request: Request,
    user_input: UserQuery,
    response: Response,
) -> QueryResponse:
    # --- Auth & input checks ---
    query_text = sanitize_text_input((user_input.query or "").strip(), max_length=1000)
    if not query_text or not validate_query_safety(query_text):
        raise HTTPException(status_code=400, detail="Invalid or empty query")
    user_id = getattr(user_input, "user_id", None)
    session_id = getattr(user_input, "session_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")

    client_ip = get_remote_address(request)
    user_agent = request.headers.get("user-agent", "unknown")

    # --- Ensure we have a valid session for this user ---
    session_data = None
    must_create = bool(getattr(user_input, "new_chat", False)) or not session_id

    if not must_create:
        session_data = SessionManager.get_session(user_id, session_id)
        if not session_data:
            must_create = True

    if must_create:
        session_id = SessionManager.create_new_session(user_id, client_ip, user_agent)
        # load the newly created session
        session_data = SessionManager.get_session(user_id, session_id)

    if not session_data:
        # Should not happen, but guard to avoid 500s
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    logger.info(f"Processing query for user {user_id}, session {session_id[:20]}: {query_text[:50]}")

    # --- Intent classification ---
    try:
        intent = classify_intent(query_text)
    except Exception:
        intent = "clarification"

    # --- ACTION REQUEST ---
    if intent == "action_request":
        details = extract_action_details_dict(query_text, session_id)
        action_details = ActionDetails(**details)
        readiness = TransactionAnalyzer.analyze_readiness(action_details)

        if not readiness["is_ready_for_execution"]:
            history = [turn.query for turn in session_data.conversation_history[-3:]]
            readiness["next_question_details"] = QuestionGenerator.generate_next_question(action_details, history)

        transaction_readiness = TransactionReadiness(**readiness)
        next_step = (
            "ready_for_confirmation" if readiness["is_ready_for_execution"]
            else "gather_final_details" if readiness["readiness_level"] == "ALMOST_READY"
            else "gather_more_information"
        )
        #This Retun would Go to Coinbasepart and then returned to frontend
        return QueryResponse(
            intent=IntentType.ACTION_REQUEST.value,
            action_details=action_details,
            transaction_readiness=transaction_readiness,
            next_step=next_step,
            confirmation_required=readiness["is_ready_for_execution"]
        )

    # --- GENERAL QUERY ---
    if intent == "general_query":
        try:
            result = run_query_chain_dict(user_id, query_text, session_id, client_ip, user_agent)
        except Exception as e:
            logger.exception("run_query_chain_dict failed: %s", e)
            raise HTTPException(status_code=500, detail="Error processing query")
        return {
            "answer": result.get("answer", "I'm not sure how to help with that."),
        }

    # --- CLARIFICATION (fallback) ---
    try:
        result = run_query_chain_dict(user_id, query_text, session_id, client_ip, user_agent)
    except Exception as e:
        logger.exception("run_query_chain_dict failed: %s", e)
        raise HTTPException(status_code=500, detail="Error processing query")

    return QueryResponse(
        clarification_question=result.get("answer", "Please provide more details."),
    )
