"""
Vector database operations with error handling and connection management.
"""

from dotenv import load_dotenv
load_dotenv()
from backend.config.settings import pinecone_settings
from backend.utils.embedding import get_embedding

from pinecone import Pinecone
from typing import List, Any
from backend.logging_setup import logger




def get_pinecone_index():
    """Initialize and return Pinecone index."""
    try:
        logger.info("Initializing Pinecone client...")
        pc = Pinecone(api_key=pinecone_settings.PINECONE_API_KEY)
        index = pc.Index(pinecone_settings.PINECONE_INDEX)
        logger.info(f"Connected to Pinecone index: {pinecone_settings.PINECONE_INDEX}")
        return index
    except Exception as e:
        logger.exception("Failed to initialize Pinecone")
        raise RuntimeError(f"Could not initialize Pinecone: {e}")
    
def query_vector_db(embedding: List[float], top_k: int = 5) -> List[Any]:
    """Query vector database with error handling."""
    if not embedding:
        raise ValueError("Embedding cannot be empty")

    if top_k <= 0 or top_k > 100:
        raise ValueError("top_k must be between 1 and 100")

    try:
        index = get_pinecone_index()
        response = index.query(vector=embedding, top_k=top_k)
        return response.matches
    except Exception as e:
        logger.error(f"Vector database query failed: {e}")
        raise RuntimeError(f"Vector search failed: {e}")
    
def db_query_chain(query: str) -> dict:
    """Process a general query using vector DB and return answer + confidence."""
    if not query or len(query) > 1000:
        raise ValueError("Query must be non-empty and less than 1000 characters")

    try:
        embedding = get_embedding(query)
        results = query_vector_db(embedding, top_k=1)
        if not results:
            return {"answer": "No relevant information found.", "confidence": 0.0}

        best_match = results[0]
        # Handle case where metadata might be None
        metadata = getattr(best_match, 'metadata', None) or {}
        answer = metadata.get("text", "")
        confidence = getattr(best_match, 'score', 0.0)

        return {
            "answer": answer if answer else "No relevant information found.",
            "confidence": confidence
        }
    except Exception as e:
        logger.error(f"General query processing failed: {e}")
        # Return fallback instead of raising exception
        return {"answer": "I couldn't find relevant information in my knowledge base.", "confidence": 0.0}

    


