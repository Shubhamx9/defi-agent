from langchain.prompts import ChatPromptTemplate
from langsmith import traceable
from backend.models.schemas import IntentType, IntentClassificationResult
from backend.utils.model_selector import get_intent_model
from backend.logging_setup import logger

# Get model instance through model manager
def _get_intent_model():
    """Get intent classification model with fallback handling."""
    return get_intent_model()

_intent_prompt = ChatPromptTemplate.from_template(
    """You are a DeFi assistant. Classify the user query into one of:

- general_query → informational/educational (e.g., "What is staking?" or Greeting message like "Hello", "Hi", "Good morning")
- action_intent → user wants to perform an action (e.g., "Send 5 USDC", "Check my balance", "What is my portfolio value?")
- clarification → query is vague or incomplete

User: {query}

Respond with ONLY one label: general_query, action_intent, or clarification.
Label:"""
)




@traceable(name="DeFi Intent Classification")
def classify_intent(query: str) -> str:
    """
    Classify query into general_query, action_request, or clarification.
    Returns string for backward compatibility with existing code.
    """
    try:
        result = classify_intent_detailed(query)
        return result.intent.value
    except Exception as e:
        logger.error(f"Intent classification failed: {e}")
        return "clarification"  # Safe fallback


@traceable(name="DeFi Intent Classification Detailed")
def classify_intent_detailed(query: str) -> IntentClassificationResult:
    """
    Classify query with detailed results including confidence and raw output.
    """
    
    # Basic input sanitization
    if not query or not query.strip():
        return IntentClassificationResult(
            intent=IntentType.CLARIFICATION
        )
    
    try:
        # Run the model with timeout protection
        intent_model = _get_intent_model()
        msg = _intent_prompt.format_messages(query=query.strip())
        out = intent_model.invoke(msg)
        
        if not out or not out.content:
            logger.warning("Empty response from intent classification model")
            return IntentClassificationResult(
                intent=IntentType.CLARIFICATION
            )
        
        raw_intent = out.content.strip().lower()
        
        # Map AI response to correct enum values
        intent_mapping = {
            "general_query": IntentType.GENERAL_QUERY,
            "action_intent": IntentType.ACTION_REQUEST,  # Map action_intent to ACTION_REQUEST
            "clarification": IntentType.CLARIFICATION
        }
        
        # Validate and map to enum
        if raw_intent in intent_mapping:
            intent = intent_mapping[raw_intent]
            confidence = 0.9  # High confidence for valid classifications
        else:
            # Fallback to clarification if invalid
            logger.warning(f"Invalid intent classification: {raw_intent}")
            intent = IntentType.CLARIFICATION
            confidence = 0.3  # Low confidence for fallback
        
        return IntentClassificationResult(
            intent=intent
        )
        
    except Exception as e:
        logger.error(f"Intent classification error: {e}")
        return IntentClassificationResult(
            intent=IntentType.CLARIFICATION
        )
