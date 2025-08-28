from backend.utils.model_selector import mini_model
from backend.logging_setup import logger
from langchain.prompts import ChatPromptTemplate
from langsmith import traceable

balance_extraction_prompt = ChatPromptTemplate.from_template(
    """Extract parameters for checking wallet balance.
    User query: {query}
    Return JSON with fields:
    - tokens (list of symbols) or "all"
    """
)

@traceable(name="Balance Extraction")
def extract_balance_parameters(query: str) -> dict:
    """
    Extract parameters for balance checking from user query.
    """
    try:
        model = mini_model()
        msg = balance_extraction_prompt.format_messages(query=query.strip())
        out = model.invoke(msg)
        if not out or not out.content:
            logger.warning("Empty response from balance extraction model")
            return {"tokens": "all"}
        # Simple parsing assuming well-formed JSON response
        import json
        return json.loads(out.content)
    except Exception as e:
        logger.error(f"Balance extraction error: {e}")
        return {"tokens": "all"}
