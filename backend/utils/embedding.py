"""
Embedding service with lazy loading and error handling.
"""
from sentence_transformers import SentenceTransformer
import logging
from typing import List, Optional
import functools

logger = logging.getLogger(__name__)

# Global model instance (lazy loaded)
_model: Optional[SentenceTransformer] = None

@functools.lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """Get embedding model with lazy loading and caching."""
    global _model
    if _model is None:
        try:
            logger.info("Loading embedding model...")
            _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise RuntimeError(f"Could not load embedding model: {e}")
    return _model

def get_embedding(text: str) -> List[float]:
    """Generate embedding vector for a text query with error handling."""
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")
    
    try:
        model = get_embedding_model()
        embedding = model.encode(text.strip()).tolist()
        return embedding
    except Exception as e:
        logger.error(f"Failed to generate embedding for text: {e}")
        raise RuntimeError(f"Embedding generation failed: {e}")

def health_check() -> bool:
    """Check if embedding model is available."""
    try:
        get_embedding_model()
        return True
    except Exception:
        return False
