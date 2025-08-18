from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Optional
from backend.models.schemas import (
    UserQuery,
    QueryResponse,
    SessionRequest,
    SessionResponse,
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
from backend.exception_handler import global_exception_handler

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


def merge_action_details(old: dict, new: dict) -> dict:
    return {**old, **{k: v for k, v in new.items() if v is not None}}


@router.post("/confirm-transaction")
@limiter.limit(f"{security_settings.RATE_LIMIT_PER_MINUTE}/minute")
def confirm_transaction(request: Request, session_id: str):
    session_data = SessionManager.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    return {
        "message": "Confirmation endpoint ready",
        "session_id": session_id,
        "note": "Implement action details retrieval from session"
    }


@router.post("/start-session", response_model=SessionResponse)
@limiter.limit(f"{security_settings.RATE_LIMIT_PER_MINUTE}/minute")
def start_session(request: Request, session_request: SessionRequest = SessionRequest()):
    client_ip = get_remote_address(request)
    user_agent = request.headers.get("user-agent", "unknown")
    session_id = SessionManager.create_new_session(client_ip, user_agent)
    logger.info(f"Manual session created: {session_id[:20]}...")
    return SessionResponse(session_id=session_id)


@router.post("/", response_model=QueryResponse)
@limiter.limit(f"{security_settings.RATE_LIMIT_PER_MINUTE}/minute")
def handle_query(request: Request, user_input: UserQuery) -> QueryResponse:
    query_text = sanitize_text_input(user_input.query.strip(), max_length=1000)
    if not query_text or not validate_query_safety(query_text):
        raise HTTPException(status_code=400, detail="Invalid or empty query")

    client_ip = get_remote_address(request)
    user_agent = request.headers.get("user-agent", "unknown")

    session_id = user_input.session_id
    session_data: Optional[SessionManager] = None
    if user_input.new_chat or not session_id:
        session_id = SessionManager.create_new_session(client_ip, user_agent)
    else:
        session_data = SessionManager.get_session(session_id)
        if not session_data:
            session_id = SessionManager.create_new_session(client_ip, user_agent)

    logger.info(f"Processing query for session {session_id[:20]}: {query_text[:50]}")

    # Intent classification
    try:
        intent = classify_intent(query_text)
    except Exception:
        intent = "clarification"

    # Action request
    # Action request
    if intent == "action_request":
        details = extract_action_details_dict(query_text, session_id)
        action_details = ActionDetails(**details)
        readiness = TransactionAnalyzer.analyze_readiness(action_details)

        if not readiness["is_ready_for_execution"] and session_data:
            history = [turn.query for turn in session_data.conversation_history[-3:]]
            readiness["next_question_details"] = QuestionGenerator.generate_next_question(action_details, history)

        transaction_readiness = TransactionReadiness(**readiness)
        next_step = (
            "ready_for_confirmation" if readiness["is_ready_for_execution"]
            else "gather_final_details" if readiness["readiness_level"] == "ALMOST_READY"
            else "gather_more_information"
        )

        return QueryResponse(
            intent=IntentType.ACTION_REQUEST.value,
            session_id=session_id,
            action_details=action_details,
            transaction_readiness=transaction_readiness,
            next_step=next_step,
            confirmation_required=readiness["is_ready_for_execution"]
        ).dict()

    # General query
    if intent == "general_query":
        result = run_query_chain_dict(session_id, query_text, client_ip)
        return QueryResponse(
            intent=IntentType.GENERAL_QUERY,
            session_id=session_id,
            answer=result.get("answer", "Unable to process request."),
            sources=result.get("sources", []),
            confidence=result.get("confidence", 0.0)
        )

    # Clarification fallback
    result = run_query_chain_dict(session_id, query_text, client_ip)
    return QueryResponse(
        intent=IntentType.CLARIFICATION,
        session_id=session_id,
        clarification_question=result.get("answer", "Please provide more details."),
        suggested_queries=result.get(
            "suggested_queries",
            ["What is DeFi?", "How do I start with yield farming?", "What are the risks in DeFi?"]
        )
    )


