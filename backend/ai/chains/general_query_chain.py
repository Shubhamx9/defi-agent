from backend.ai.chains.db_query_chain import db_query_chain
from backend.logging_setup import logger
from backend.utils.model_selector import tiny_model, mini_model




def gpt_tiny_response(query: str, context: str) -> str:
    """Generate rephrased response using the tiny model."""
    model = tiny_model()
    prompt = (
        "You are a DeFi assistant. "
        "Rephrase the following answer with a cautious/uncertain tone. "
        "Respond only if the query is strictly about Decentralized Finance (DeFi). "
        "If the query is not about DeFi, reply with: 'I can only answer DeFi-related questions.'\n\n"
        f"Query: {query}\n\n"
        f"Answer: {context}\n\n"
        "Rephrased Answer:"
    )

    try:
        response = model.invoke(prompt)
        # Extract string content from AIMessage object
        if hasattr(response, 'content'):
            return response.content
        return str(response)
    except Exception as e:
        logger.error(f"Tiny model prediction failed: {e}")
        return "I can only answer DeFi-related questions."


def gpt_mini_response(query: str) -> str:
    """Placeholder for GPT mini response generation."""
    model = mini_model()
    prompt = (
        "You are a DeFi assistant. "
        "Respond only to queries strictly related to Decentralized Finance (DeFi). "
        "If the query is not about DeFi, respond with: 'I can only answer DeFi-related questions.'\n\n"
        f"Query: {query}\n\n"
        "Answer:"
    )
    try:
        response = model.invoke(prompt)
        # Extract string content from AIMessage object
        if hasattr(response, 'content'):
            return response.content
        return str(response)
    except Exception as e:
        logger.error(f"Mini model prediction failed: {e}")
        return "I can only answer DeFi-related questions."


def general_query_chain(query: str) -> str:
    """Process a general query and return an answer."""
    try:
        res = db_query_chain(query)   # returns a dict
        result = res["answer"]
        confidence = res["confidence"]

        if confidence > 0.98:
            return result
        elif confidence > 0.90:
            # USE GPT tiny to rephrase with uncertainty
            return gpt_tiny_response(query, result)
        else:
            # USE GPT mini to give generalized answer
            return gpt_mini_response(query)
    except Exception as e:
        logger.log(40, f"Replying directly using model: {e}")
        return gpt_mini_response(query)


