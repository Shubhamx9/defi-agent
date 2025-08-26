from langchain.prompts import ChatPromptTemplate
from langsmith import traceable
from backend.models.schemas import IntentType, IntentClassificationResult
from backend.utils.model_selector import get_intent_model
from typing import Union
from backend.logging_setup import logger
from backend.utils.embedding import get_embedding
from backend.utils.vector_db import query_vector_db


# Get model instance through model manager
def _get_intent_model():
    """Get intent classification model with fallback handling."""
    return get_intent_model()

_intent_prompt = ChatPromptTemplate.from_template(
    """You are a DeFi assistant who Classify queries as:
- general_query (info/education)
- action_request (wants DeFi action or Information about current APY)
- clarification (unclear)

User: {query}

These classicifications are mutually exclusive. Only respond with one of the three labels.: 
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
    import logging
    logger = logging.getLogger(__name__)
    
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
        
        # Validate and map to enum
        try:
            intent = IntentType(raw_intent)
            confidence = 0.9  # High confidence for valid classifications
        except ValueError:
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
