from fastapi import APIRouter, HTTPException, Request, Response
from slowapi import Limiter
from slowapi.util import get_remote_address
from backend.config.settings import security_settings

from backend.models.schemas import (
    UserQuery,
    QueryResponse
)
from backend.middleware.input_sanitizer import sanitize_text_input, validate_query_safety
from backend.ai.chains.intent_chain import classify_intent
from backend.ai.chains.general_query_chain import general_query_chain
from backend.logging_setup import logger
from backend.ai.chains.run_action_chain import run_action_chain





router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post("/", response_model = QueryResponse)
@limiter.limit(f"{security_settings.RATE_LIMIT_PER_MINUTE}/minute")
def handle_query(
    request: Request,
    user_input: UserQuery,
    response: Response,
) -> QueryResponse:
    """
    Handle a query to the DeFi AI Assistant.
    """
    query_text = sanitize_text_input((user_input.query or "").strip(), max_length=1000)
    if not query_text or not validate_query_safety(query_text):
        raise HTTPException(status_code=400, detail="Invalid or empty query")
    user_id = getattr(user_input, "user_id", None)
    # session_id = getattr(user_input, "session_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    client_ip = get_remote_address(request)
    user_agent = request.headers.get("user-agent", "unknown")

    #Send For Intent Classicfication
    intent = classify_intent(query_text)

    if intent == "general_query":
        try:
            answer = general_query_chain(query_text)
            return QueryResponse(answer=answer)
        except Exception as e:
            logger.error(f"Error processing general query: {e}")
            raise HTTPException(status_code=500, detail="Error processing query")
            return QueryResponse(
                answer="Sorry, I couldn't process your query at this time.",
            )
    
    elif intent == "clarification":
        answer = "Could you please clarify your question?"
        return QueryResponse(answer=answer)
    
    elif intent == "action_intent":
        # Check if wallet data is provided for action intents
        if not user_input.wallet_address or not user_input.wallet_secret:
            return QueryResponse(
                answer="🔐 To perform blockchain actions, please provide your wallet address and private key with your request. For general questions about DeFi, I can help without wallet access."
            )
        
        # Pass wallet data to action chain
        answer = run_action_chain(query_text, user_id, user_input.wallet_address, user_input.wallet_secret)
        return QueryResponse(answer=answer)


    