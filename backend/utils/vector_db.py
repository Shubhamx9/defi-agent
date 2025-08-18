"""
Vector database operations with error handling and connection management.
"""
from pinecone import Pinecone
from dotenv import load_dotenv
import logging
from typing import List, Any
load_dotenv()
from backend.config.settings import pinecone_settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Pinecone client & index at import
try:
    logger.info("Initializing Pinecone client...")
    pc = Pinecone(api_key=pinecone_settings.PINECONE_API_KEY)
    index = pc.Index(pinecone_settings.PINECONE_INDEX)
    logger.info(f"Connected to Pinecone index: {pinecone_settings.PINECONE_INDEX}")
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
        response = index.query(vector=embedding, top_k=top_k)
        return response.matches
    except Exception as e:
        logger.exception("Vector database query failed")
        raise RuntimeError(f"Vector search failed: {e}")


import logging

logger = logging.getLogger(__name__)

def health_check() -> bool:
    """Check Pinecone connection health. Never crash."""
    try:
        from backend.utils.vector_db import index  # lazy import
        if index is None:
            logger.warning("Pinecone index is not initialized")
            return False

        # Lightweight connectivity check
        index.describe_index_stats()
        logger.info("Pinecone health check successful")
        return True
    except Exception as e:
        logger.warning(f"Pinecone health check failed: {e}")
        return False
