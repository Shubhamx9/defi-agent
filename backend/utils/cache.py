# Redis cache
import redis
from backend.config.settings import settings

# Connect to Redis
r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    decode_responses=True
)

def get_cached_response(key: str):
    """Retrieve cached response for a key."""
    return r.get(key)

def set_cached_response(key: str, value: str, ttl: int = 3600):
    """Cache response with TTL in seconds."""
    r.set(key, value, ex=ttl)
