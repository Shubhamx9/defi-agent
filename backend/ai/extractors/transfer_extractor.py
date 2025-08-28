from backend.utils.model_selector import mini_model
from backend.logging_setup import logger
from langchain.prompts import ChatPromptTemplate
from langsmith import traceable
import json

# Updated prompt to explicitly return null for missing fields
transfer_extraction_prompt = ChatPromptTemplate.from_template(
    """Extract parameters for sending tokens.
    User query: {query}
    
    Return a JSON object with the following fields:
    - "amount": The numerical amount to send.
    - "token": The token's symbol (e.g., "ETH", "USDC").
    - "recipient": The recipient's Ethereum address. If not mentioned, return null.
    """
)

@traceable(name="Transfer Extraction")
def extract_transfer_parameters(query: str) -> dict:
    """
    Extract parameters for token transfer from user query.
    Returns None for missing parameters.
    """
    # Define a default response with None for missing values
    default_response = {"amount": None, "token": None, "recipient": None}
    
    try:
        model = mini_model()
        msg = transfer_extraction_prompt.format_messages(query=query.strip())
        out = model.invoke(msg)
        
        if not out or not out.content:
            logger.warning("Empty response from transfer extraction model")
            return default_response
            
        extracted_data = json.loads(out.content)
        # Merge extracted data with defaults to ensure all keys exist
        return {**default_response, **extracted_data}
        
    except Exception as e:
        logger.error(f"Transfer extraction error: {e}")
        return default_response