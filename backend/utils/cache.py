"""
Redis cache with connection pooling and error handling.
"""
import redis
import logging
from typing import Optional
from backend.config.settings import settings

logger = logging.getLogger(__name__)

# Connection pool for better performance
_redis_pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    decode_responses=True,
    max_connections=20,
    retry_on_timeout=True,
    socket_connect_timeout=5,
    socket_timeout=5
)

def get_redis_client():
    """Get Redis client with connection pool."""
    return redis.Redis(connection_pool=_redis_pool)

def get_cached_response(key: str) -> Optional[str]:
    """Retrieve cached response for a key with error handling."""
    try:
        r = get_redis_client()
        return r.get(key)
    except redis.RedisError as e:
        logger.warning(f"Redis get failed for key {key}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in Redis get for key {key}: {e}")
        return None

def set_cached_response(key: str, value: str, ttl: int = 3600) -> bool:
    """Cache response with TTL in seconds. Returns success status."""
    try:
        r = get_redis_client()
        r.set(key, value, ex=ttl)
        return True
    except redis.RedisError as e:
        logger.warning(f"Redis set failed for key {key}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in Redis set for key {key}: {e}")
        return False

def health_check() -> bool:
    """Check Redis connection health."""
    try:
        r = get_redis_client()
        r.ping()
        return True
    except Exception:
        return False
