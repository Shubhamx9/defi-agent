"""
SessionManager: secure session IDs, TTL-based expiration, and IP-based limits.
"""
import time
import secrets
import hashlib
import uuid
from typing import Optional, Dict, Any
from backend.models.schemas import SessionData
from backend.utils.cache import get_cached_response, set_cached_response, get_redis_client
import logging

logger = logging.getLogger(__name__)

SESSION_TTL = 3600  # 1 hour
MAX_SESSIONS_PER_IP = 10

class SessionManager:
    @staticmethod
    def generate_session_id() -> str:
        timestamp = str(int(time.time() * 1000))
        random_part = secrets.token_hex(16)
        unique_salt = str(uuid.uuid4()).replace("-", "")
        hash_part = hashlib.sha256(f"{timestamp}-{random_part}-{unique_salt}".encode()).hexdigest()[:16]
        session_id = f"{timestamp}-{random_part}-{hash_part}"
        logger.debug(f"Generated session ID: {session_id[:20]}...")
        return session_id

    @staticmethod
    def get_session_key(session_id: str) -> str:
        return f"chat_session:{session_id}"

    @staticmethod
    def get_ip_count_key(ip: str) -> str:
        return f"ip_sessions_count:{ip}"

    @staticmethod
    def create_new_session(ip: str, user_agent: str = None) -> str:
        r = get_redis_client()
        ip_key = SessionManager.get_ip_count_key(ip)
        count = r.get(ip_key)
        if count and int(count) >= MAX_SESSIONS_PER_IP:
            raise ValueError(f"IP {ip} has too many active sessions")

        session_id = SessionManager.generate_session_id()
        session_data = SessionData(
            user_id=session_id,
            last_updated=time.time(),
            metadata={
                "ip": ip,
                "user_agent": user_agent,
                "created_at": time.time(),
            }
        )

        # Save session
        set_cached_response(SessionManager.get_session_key(session_id), session_data.dict(), ttl=SESSION_TTL)
        # Increment IP count with TTL
        r.incr(ip_key)
        r.expire(ip_key, SESSION_TTL)

        logger.info(f"Created new session: {session_id[:20]} for IP {ip}")
        return session_id

    @staticmethod
    def get_session(session_id: str) -> Optional[SessionData]:
        raw = get_cached_response(SessionManager.get_session_key(session_id))
        if not raw:
            return None
        try:
            return SessionData(**raw)
        except Exception as e:
            logger.error(f"Failed to parse session {session_id[:20]}: {e}")
            SessionManager.delete_session(session_id)
            return None

    @staticmethod
    def update_session(session_id: str, session_data: SessionData):
        session_data.last_updated = time.time()
        set_cached_response(SessionManager.get_session_key(session_id), session_data.dict(), ttl=SESSION_TTL)

    @staticmethod
    def delete_session(session_id: str):
        r = get_redis_client()
        session = get_cached_response(SessionManager.get_session_key(session_id))
        if session:
            ip = session.get("metadata", {}).get("ip")
            if ip:
                r.decr(SessionManager.get_ip_count_key(ip))
        r.delete(SessionManager.get_session_key(session_id))
        logger.info(f"Deleted session: {session_id[:20]}")

    @staticmethod
    def get_session_stats() -> Dict[str, Any]:
        r = get_redis_client()
        session_keys = r.keys("chat_session:*")
        ip_keys = r.keys("ip_sessions_count:*")
        return {
            "active_sessions": len(session_keys),
            "active_ips": len(ip_keys),
            "session_ttl": SESSION_TTL,
            "max_sessions_per_ip": MAX_SESSIONS_PER_IP
        }
