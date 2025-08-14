from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from backend.models.schemas import (
    UserQuery, 
    QueryResponse, 
    SessionRequest, 
    SessionResponse,
    ActionDetails,
    IntentType,
    ErrorResponse
)
from backend.ai.chains.intent_chain import classify_intent
from backend.ai.chains.query_chain import run_query_chain_dict
from backend.ai.chains.action_extraction_chain import extract_action_details_dict
from backend.middleware.input_sanitizer import sanitize_text_input, validate_query_safety
from backend.config.settings import settings
import json
from backend.utils.cache import get_cached_response, set_cached_response
import uuid
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

router = APIRouter()

SESSION_TTL = 3600  # 1 hour

def merge_action_details(old: dict, new: dict) -> dict:
    """Merge new action details into old, preferring new values if present."""
    merged = old.copy()
    for k, v in new.items():
        if v is not None:
            merged[k] = v
    return merged

@router.post("/start-session", response_model=SessionResponse)
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
def start_session(request: Request, session_request: SessionRequest = SessionRequest()):
    """Start a new session and return a unique session_id."""
    try:
        session_id = str(uuid.uuid4())
        logger.info(f"New session created: {session_id}")
        return SessionResponse(session_id=session_id)
    except Exception as e:
        logger.error(f"Session creation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to create session")

@router.post("/", response_model=QueryResponse)
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
def handle_query(request: Request, user_input: UserQuery) -> QueryResponse:
    """Handle user queries and return appropriate responses based on intent."""
    try:
        # Input sanitization and validation
        q = sanitize_text_input(user_input.query.strip(), max_length=1000)
        if not q:
            raise HTTPException(status_code=400, detail="Empty query")
        
        # Additional safety validation
        if not validate_query_safety(q):
            raise HTTPException(status_code=400, detail="Query contains suspicious patterns")

        session_id = user_input.session_id
        logger.info(f"Processing query for session {session_id}: {q[:50]}...")
        
        # Classify intent with error handling
        try:
            intent = classify_intent(q)
        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            intent = "clarification"

        if intent == "action_request":
            try:
                # Use session_id as user_id for action extraction
                user_id = session_id or "anonymous"
                details_dict = extract_action_details_dict(q, user_id)
                
                # Convert dict to ActionDetails model
                action_details = ActionDetails(**details_dict)
                
                return QueryResponse(
                    intent=IntentType.ACTION_REQUEST,
                    session_id=session_id,
                    action_details=action_details,
                    next_step="fetch_apy_and_confirm",
                    confirmation_required=True
                )
            except Exception as e:
                logger.error(f"Action extraction failed: {e}")
                # Fallback to general query processing
                intent = "general_query"

        if intent == "general_query":
            try:
                # Use session_id as user_id for query chain
                user_id = session_id or "anonymous"
                result = run_query_chain_dict(user_id, q)
                return QueryResponse(
                    intent=IntentType.GENERAL_QUERY,
                    session_id=session_id,
                    answer=result.get("answer", "I'm having trouble processing your request right now."),
                    sources=result.get("sources", []),
                    confidence=result.get("confidence", 0.0)
                )
            except Exception as e:
                logger.error(f"Query processing failed: {e}")
                return QueryResponse(
                    intent=IntentType.CLARIFICATION,
                    session_id=session_id,
                    clarification_question="I'm experiencing technical difficulties. Could you please rephrase your question?",
                    suggested_queries=[]
                )

        else:  # clarification or unknown
            try:
                user_id = session_id or "anonymous"
                result = run_query_chain_dict(user_id, q)
                return QueryResponse(
                    intent=IntentType.CLARIFICATION,
                    session_id=session_id,
                    clarification_question=result.get("answer", "Could you please provide more details?"),
                    suggested_queries=result.get("suggested_queries", [])
                )
            except Exception as e:
                logger.error(f"Clarification processing failed: {e}")
                return QueryResponse(
                    intent=IntentType.CLARIFICATION,
                    session_id=session_id,
                    clarification_question="Could you please rephrase your question?",
                    suggested_queries=["What is DeFi?", "How do I start with yield farming?", "What are the risks in DeFi?"]
                )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in handle_query: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
