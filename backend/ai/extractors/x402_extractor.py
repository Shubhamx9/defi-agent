import json
from backend.utils.model_selector import mini_model
from backend.logging_setup import logger
from langchain.prompts import ChatPromptTemplate
from langsmith import traceable

# Define a clear prompt template for the language model.
# This guides the model to extract the specific x402 parameters in a structured JSON format.
x402_extraction_prompt = ChatPromptTemplate.from_template(
    """Extract x402 payment parameters from the user's request for a digital service.
    
User query: {query}

Return a JSON object with the following fields:
- "service": Identify the service type. Should be one of "api_access", "data_feed", "oracle_query", or "generic_service" if unclear.
- "amount": The numerical payment amount. Return null if not specified.
- "token": The payment token symbol (e.g., "ETH", "USDC"). Default to "ETH" if not mentioned.
- "recipient": The recipient's Ethereum address (e.g., "0x..."). Return null if not provided.
"""
)

@traceable(name="X402 Parameter Extraction")
def extract_x402_parameters(query: str) -> dict:
    """
    Extracts x402 payment parameters from a user query using a language model.
    """
    # Define a default response structure for error handling and consistency.
    default_response = {
        "service": "generic_service",
        "amount": None,
        "token": "ETH",
        "recipient": None
    }
    
    try:
        # Initialize the language model.
        model = mini_model()
        
        # Format the prompt with the user's query.
        prompt_messages = x402_extraction_prompt.format_messages(query=query.strip())
        
        # Invoke the model to get the structured data.
        model_output = model.invoke(prompt_messages)
        
        # Validate the model's response.
        if not model_output or not model_output.content:
            logger.warning("Empty response from x402 extraction model for query: '%s'", query)
            return default_response
            
        # Parse the JSON string from the model's content.
        extracted_data = json.loads(model_output.content)
        
        # Ensure the response contains expected keys, merging with defaults.
        return {**default_response, **extracted_data}

    except json.JSONDecodeError as e:
        logger.error(
            "JSON parsing failed for x402 extraction. Raw model output: %s. Error: %s",
            getattr(model_output, 'content', 'N/A'), e
        )
        return default_response
    except Exception as e:
        logger.error("An unexpected error occurred during x402 extraction: %s", e)
        return default_response