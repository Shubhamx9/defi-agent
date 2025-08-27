from backend.utils.model_selector import mini_model
from backend.logging_setup import logger
from langchain.prompts import ChatPromptTemplate
from langsmith import traceable


price_extraction_prompt = (
    "You are a strict extractor. Extract the cryptocurrency symbol or trading pair "
    "from the user query. If no valid token/pair is found, return 'None'.\n\n"
    "Query: {query}\n\n"
    "Return JSON ONLY in this format:\n"
    "{{\"symbol\": <string or None>}}"
)

@traceable(name="Price Extraction")
def extract_price_parameters(query: str) -> dict:
    """
    Extract parameters for price checking from user query.
    """
    try:
        model = mini_model()
        msg = ChatPromptTemplate.from_template(price_extraction_prompt).format_messages(query=query.strip())
        out = model.invoke(msg)
        if not out or not out.content:
            logger.warning("Empty response from price extraction model")
            return {"symbol": None}
        # Simple parsing assuming well-formed JSON response
        import json
        return json.loads(out.content)
    except Exception as e:
        logger.error(f"Price extraction error: {e}")
        return {"symbol": None}
