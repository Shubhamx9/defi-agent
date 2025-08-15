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
    ErrorResponse,
    TransactionReadiness
)
from backend.ai.chains.intent_chain import classify_intent
from backend.ai.chains.query_chain import run_query_chain_dict
from backend.ai.chains.action_extraction_chain import extract_action_details_dict
from backend.middleware.input_sanitizer import sanitize_text_input, validate_query_safety
from backend.config.settings import settings
import json
from backend.utils.session_manager import SessionManager
from backend.utils.transaction_analyzer import TransactionAnalyzer
from backend.utils.question_generator import QuestionGenerator
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

router = APIRouter()

def merge_action_details(old: dict, new: dict) -> dict:
    """Merge new action details into old, preferring new values if present."""
    merged = old.copy()
    for k, v in new.items():
        if v is not None:
            merged[k] = v
    return merged

@router.post("/confirm-transaction")
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
def confirm_transaction(request: Request, session_id: str):
    """Generate detailed confirmation summary for ready transactions."""
    try:
        client_ip = get_remote_address(request)
        
        # Get session data
        session_data = SessionManager.get_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found or expired")
        
        # Get latest action details from session
        # This would typically be stored in session metadata
        # For now, return a placeholder - you'd implement session-based action storage
        
        return {
            "message": "Confirmation endpoint ready",
            "session_id": session_id,
            "note": "Implement action details retrieval from session"
        }
        
    except Exception as e:
        logger.error(f"Confirmation generation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate confirmation")

@router.post("/start-session", response_model=SessionResponse)
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
def start_session(request: Request, session_request: SessionRequest = SessionRequest()):
    """Create a new session (deprecated - sessions are now auto-created)."""
    try:
        client_ip = get_remote_address(request)
        user_agent = request.headers.get("user-agent", "unknown")
        
        session_id = SessionManager.create_new_session(client_ip, user_agent)
        logger.info(f"Manual session created: {session_id[:20]}...")
        return SessionResponse(session_id=session_id)
    except Exception as e:
        logger.error(f"Session creation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to create session")

@router.post("/", response_model=QueryResponse)
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
def handle_query(request: Request, user_input: UserQuery) -> QueryResponse:
    """Handle user queries with automatic session management."""
    try:
        # Input sanitization and validation
        q = sanitize_text_input(user_input.query.strip(), max_length=1000)
        if not q:
            raise HTTPException(status_code=400, detail="Empty query")
        
        # Additional safety validation
        if not validate_query_safety(q):
            raise HTTPException(status_code=400, detail="Query contains suspicious patterns")

        # Auto-session management
        client_ip = get_remote_address(request)
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Handle session logic
        session_id = user_input.session_id
        session_data = None
        
        # Check if new chat is requested or no session provided
        if user_input.new_chat or not session_id:
            # Create new session
            session_id = SessionManager.create_new_session(client_ip, user_agent)
            logger.info(f"Auto-created new session: {session_id[:20]}...")
        else:
            # Try to get existing session
            session_data = SessionManager.get_session(session_id)
            if not session_data:
                # Session expired or invalid, create new one
                session_id = SessionManager.create_new_session(client_ip, user_agent)
                logger.info(f"Session expired, created new: {session_id[:20]}...")
        
        logger.info(f"Processing query for session {session_id[:20]}...: {q[:50]}...")
        
        # Classify intent with error handling
        try:
            intent = classify_intent(q)
        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            intent = "clarification"

        if intent == "action_request":
            try:
                # Use session_id for action extraction
                details_dict = extract_action_details_dict(q, session_id)
                
                # Convert dict to ActionDetails model
                action_details = ActionDetails(**details_dict)
                
                # Analyze transaction readiness
                readiness_analysis = TransactionAnalyzer.analyze_readiness(action_details)
                
                # Generate intelligent next question if not ready
                if not readiness_analysis["is_ready_for_execution"]:
                    # Get conversation history from session for context
                    conversation_history = []
                    if session_data and hasattr(session_data, 'conversation_history'):
                        conversation_history = [turn.query for turn in session_data.conversation_history[-3:]]
                    
                    next_question = QuestionGenerator.generate_next_question(action_details, conversation_history)
                    readiness_analysis["next_question_details"] = next_question
                
                transaction_readiness = TransactionReadiness(**readiness_analysis)
                
                # Determine next step based on readiness
                if readiness_analysis["is_ready_for_execution"]:
                    next_step = "ready_for_confirmation"
                elif readiness_analysis["readiness_level"] == "ALMOST_READY":
                    next_step = "gather_final_details"
                else:
                    next_step = "gather_more_information"
                
                return QueryResponse(
                    intent=IntentType.ACTION_REQUEST,
                    session_id=session_id,
                    action_details=action_details,
                    transaction_readiness=transaction_readiness,
                    next_step=next_step,
                    confirmation_required=readiness_analysis["is_ready_for_execution"]
                )
            except Exception as e:
                logger.error(f"Action extraction failed: {e}")
                # Fallback to general query processing
                intent = "general_query"

        if intent == "general_query":
            try:
                # Use session_id for query chain with IP tracking
                result = run_query_chain_dict(session_id, q, client_ip)
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
                result = run_query_chain_dict(session_id, q, client_ip)
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
