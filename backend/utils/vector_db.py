"""
Vector database operations with error handling and connection management.
"""
from pinecone import Pinecone
from dotenv import load_dotenv
import logging
from typing import List, Optional
import functools
from backend.config.settings import settings

load_dotenv()
logger = logging.getLogger(__name__)

# Global Pinecone client (lazy loaded)
_pinecone_client: Optional[Pinecone] = None
_pinecone_index = None

@functools.lru_cache(maxsize=1)
def get_pinecone_client() -> Pinecone:
    """Get Pinecone client with lazy loading."""
    global _pinecone_client
    if _pinecone_client is None:
        try:
            logger.info("Initializing Pinecone client...")
            _pinecone_client = Pinecone(api_key=settings.PINECONE_API_KEY)
            logger.info("Pinecone client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone client: {e}")
            raise RuntimeError(f"Could not connect to Pinecone: {e}")
    return _pinecone_client

def get_pinecone_index():
    """Get Pinecone index with lazy loading."""
    global _pinecone_index
    if _pinecone_index is None:
        try:
            pc = get_pinecone_client()
            _pinecone_index = pc.Index(settings.PINECONE_INDEX)
            logger.info(f"Connected to Pinecone index: {settings.PINECONE_INDEX}")
        except Exception as e:
            logger.error(f"Failed to connect to Pinecone index: {e}")
            raise RuntimeError(f"Could not connect to Pinecone index: {e}")
    return _pinecone_index

def query_vector_db(embedding: List[float], top_k: int = 5):
    """Query vector database with error handling."""
    if not embedding:
        raise ValueError("Embedding cannot be empty")
    
    if top_k <= 0 or top_k > 100:
        raise ValueError("top_k must be between 1 and 100")
    
    try:
        index = get_pinecone_index()
        response = index.query(
            vector=embedding,
            top_k=top_k,
            include_metadata=True,
            include_values=False
        )
        return response.matches
    except Exception as e:
        logger.error(f"Vector database query failed: {e}")
        raise RuntimeError(f"Vector search failed: {e}")

def health_check() -> bool:
    """Check Pinecone connection health."""
    try:
        index = get_pinecone_index()
        # Try a simple query to test connection
        index.describe_index_stats()
        return True
    except Exception:
        return False
