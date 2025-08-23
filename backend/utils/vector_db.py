"""
Vector database operations with error handling and connection management.
"""
from pinecone import Pinecone
from dotenv import load_dotenv
from typing import List, Any
from backend.config.settings import pinecone_settings
from backend.logging_setup import setup_logger

load_dotenv()

# Setup logger
logger = setup_logger()


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


def health_check() -> bool:
    """Check Pinecone connection health. Never crash."""
    try:
        index = get_pinecone_index()
        index.describe_index_stats()
        logger.info("Pinecone health check successful")
        return True
    except Exception as e:
        logger.warning(f"Pinecone health check failed: {e}")
        return False
