"""
SessionManager: secure session IDs, TTL-based expiration, and user_id-based session limits (atomic).
"""
import time
import secrets
import hashlib
import uuid
import json
from typing import Optional, Dict, Any
from backend.models.schemas import SessionData
from backend.utils.cache import get_cached_response, set_cached_response, get_redis_client
from backend.logging_setup import logger

SESSION_TTL = 1800  # 30 mins
MAX_SESSIONS_PER_USER = 10

# Lua script: atomically INCR user session count iff below limit; set TTL.
# Returns: -1 if over limit, else new count.
INCR_IF_BELOW_LIMIT = """
local key    = KEYS[1]
local limit  = tonumber(ARGV[1])
local ttl    = tonumber(ARGV[2])
local cur    = tonumber(redis.call('GET', key) or '0')
if cur >= limit then
  return -1
else
  local newv = redis.call('INCR', key)
  redis.call('EXPIRE', key, ttl)
  return newv
end
"""

class SessionManager:
    @staticmethod
    def generate_session_id() -> str:
        """Generate a cryptographically secure session ID"""
        timestamp = str(int(time.time() * 1000))
        random_part = secrets.token_hex(16)
        unique_salt = str(uuid.uuid4()).replace("-", "")
        hash_part = hashlib.sha256(
            f"{timestamp}-{random_part}-{unique_salt}".encode()
        ).hexdigest()[:16]
        return f"{timestamp}-{random_part}-{hash_part}"

    @staticmethod
    def get_session_key(user_id: str, session_id: str) -> str:
        return f"user_session:{user_id}:{session_id}"

    @staticmethod
    def get_user_count_key(user_id: str) -> str:
        return f"user_sessions_count:{user_id}"

    @staticmethod
    def create_new_session(user_id: str, ip: str, user_agent: str = None) -> str:
        """
        Create a new session tied to user_id, stored in Redis, limited per user.
        Uses a Lua script to enforce the per-user session cap atomically.
        """
        r = get_redis_client()

        # 1) Atomically bump per-user count only if below limit
        incr_script = r.register_script(INCR_IF_BELOW_LIMIT)
        result = incr_script(keys=[SessionManager.get_user_count_key(user_id)],
                             args=[MAX_SESSIONS_PER_USER, SESSION_TTL])
        if int(result) == -1:
            raise ValueError(f"User {user_id} has too many active sessions")

        # 2) Create session object and store with TTL
        session_id = SessionManager.generate_session_id()
        now = time.time()
        session_data = SessionData(
            user_id=user_id,
            last_updated=now,
            metadata={
                "schema_version": 1,
                "first_ip": ip,
                "last_ip": ip,
                "user_agent": user_agent,
                "created_at": now,
            },
        )

        # Use existing cache helper for consistency (handles JSON + TTL)
        set_cached_response(
            SessionManager.get_session_key(user_id, session_id),
            json.dumps(session_data.dict()),
            ttl=SESSION_TTL,
        )

        logger.info(f"Created new session {session_id[:20]} for user {user_id}")
        return session_id

    @staticmethod
    def get_session(user_id: str, session_id: str) -> Optional[SessionData]:
        """Retrieve session if valid"""
        raw = get_cached_response(SessionManager.get_session_key(user_id, session_id))
        if not raw:
            return None
        return SessionData(**json.loads(raw))

    @staticmethod
    def update_session(user_id: str, session_id: str, session_data: SessionData, ip_address: Optional[str] = None):
        """Refresh TTL and update metadata (only last_ip and last_updated)"""
        session_key = SessionManager.get_session_key(user_id, session_id)
        r = get_redis_client()
        if not r.exists(session_key):
            # expired or deleted: do not recreate silently
            return
        session_data.last_updated = time.time()
        if ip_address:
            session_data.metadata["last_ip"] = ip_address
        set_cached_response(session_key, session_data.dict(), ttl=SESSION_TTL)

    @staticmethod
    def delete_session(user_id: str, session_id: str):
        """Remove a session from Redis and safely decrement per-user count (no negatives)."""
        r = get_redis_client()
        session_key = SessionManager.get_session_key(user_id, session_id)
        session = get_cached_response(session_key)

        # Delete the session key first
        r.delete(session_key)

        # Safely decrement the per-user counter if it exists and > 0
        user_key = SessionManager.get_user_count_key(user_id)
        try:
            cur = int(r.get(user_key) or 0)
            if cur > 0:
                r.decr(user_key)
        except Exception:
            # If anything odd happens, avoid throwing in cleanup
            pass

        logger.info(f"Deleted session {session_id[:20]} for user {user_id}")

    @staticmethod
    def get_session_stats() -> Dict[str, Any]:
        """Basic stats for monitoring (use SCAN instead of KEYS)."""
        r = get_redis_client()
        # SCAN for user_session:* keys
        session_count = 0
        cursor = 0
        while True:
            cursor, keys = r.scan(cursor=cursor, match="user_session:*", count=1000)
            session_count += len(keys)
            if cursor == 0:
                break

        # SCAN for counters
        user_count = 0
        cursor = 0
        while True:
            cursor, keys = r.scan(cursor=cursor, match="user_sessions_count:*", count=1000)
            user_count += len(keys)
            if cursor == 0:
                break

        return {
            "active_sessions": session_count,
            "active_users": user_count,
            "session_ttl": SESSION_TTL,
            "max_sessions_per_user": MAX_SESSIONS_PER_USER,
        }
