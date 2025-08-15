"""
Advanced session management with auto-generation and user isolation.
"""
import uuid
import time
import hashlib
import secrets
from typing import Optional, Dict, Any
from backend.utils.cache import get_cached_response, set_cached_response
from backend.models.schemas import SessionData
import json
import logging

logger = logging.getLogger(__name__)

# Session configuration
SESSION_TTL = 3600  # 1 hour in seconds
SESSION_CLEANUP_INTERVAL = 300  # 5 minutes
MAX_SESSIONS_PER_IP = 10  # Prevent abuse

class SessionManager:
    """Advanced session management with auto-generation and cleanup."""
    
    @staticmethod
    def generate_session_id() -> str:
        """
        Generate a cryptographically secure, long session ID.
        Format: timestamp-random-hash (ensures uniqueness across time and users)
        """
        timestamp = str(int(time.time() * 1000))  # Millisecond precision
        random_part = secrets.token_hex(16)  # 32 character random hex
        unique_salt = str(uuid.uuid4()).replace('-', '')  # Additional uniqueness
        
        # Create hash for additional security and length
        combined = f"{timestamp}-{random_part}-{unique_salt}"
        hash_part = hashlib.sha256(combined.encode()).hexdigest()[:16]
        
        # Final session ID: timestamp-random-hash (64+ characters)
        session_id = f"{timestamp}-{random_part}-{hash_part}"
        
        logger.info(f"Generated new session ID: {session_id[:20]}...")
        return session_id
    
    @staticmethod
    def get_session_key(session_id: str) -> str:
        """Get Redis key for session storage."""
        return f"chat_session:{session_id}"
    
    @staticmethod
    def get_ip_sessions_key(ip_address: str) -> str:
        """Get Redis key for tracking sessions per IP."""
        return f"ip_sessions:{ip_address}"
    
    @staticmethod
    def create_new_session(ip_address: str, user_agent: str = None) -> str:
        """
        Create a new session with proper tracking and limits.
        
        Args:
            ip_address: Client IP address for abuse prevention
            user_agent: Client user agent for additional tracking
            
        Returns:
            New session ID
        """
        # Check session limits per IP
        ip_sessions_key = SessionManager.get_ip_sessions_key(ip_address)
        existing_sessions = get_cached_response(ip_sessions_key)
        
        if existing_sessions:
            try:
                sessions_list = json.loads(existing_sessions)
                if len(sessions_list) >= MAX_SESSIONS_PER_IP:
                    # Clean up old sessions first
                    SessionManager.cleanup_old_sessions(sessions_list)
                    
                    # Re-check after cleanup
                    if len(sessions_list) >= MAX_SESSIONS_PER_IP:
                        logger.warning(f"IP {ip_address} has too many active sessions")
                        # Remove oldest session
                        oldest_session = sessions_list.pop(0)
                        SessionManager.delete_session(oldest_session)
            except json.JSONDecodeError:
                sessions_list = []
        else:
            sessions_list = []
        
        # Generate new session
        session_id = SessionManager.generate_session_id()
        
        # Create session data
        session_data = SessionData(
            user_id=session_id,
            last_updated=time.time(),
            metadata={
                "ip_address": ip_address,
                "user_agent": user_agent,
                "created_at": time.time(),
                "last_activity": time.time()
            }
        )
        
        # Store session
        session_key = SessionManager.get_session_key(session_id)
        set_cached_response(session_key, json.dumps(session_data.dict()), ttl=SESSION_TTL)
        
        # Track session for this IP
        sessions_list.append({
            "session_id": session_id,
            "created_at": time.time(),
            "last_activity": time.time()
        })
        set_cached_response(ip_sessions_key, json.dumps(sessions_list), ttl=SESSION_TTL)
        
        logger.info(f"Created new session for IP {ip_address}: {session_id[:20]}...")
        return session_id
    
    @staticmethod
    def get_session(session_id: str) -> Optional[SessionData]:
        """
        Get session data with automatic cleanup of expired sessions.
        
        Args:
            session_id: Session identifier
            
        Returns:
            SessionData if valid, None if expired or not found
        """
        if not session_id:
            return None
        
        session_key = SessionManager.get_session_key(session_id)
        raw_data = get_cached_response(session_key)
        
        if not raw_data:
            logger.info(f"Session not found: {session_id[:20]}...")
            return None
        
        try:
            data = json.loads(raw_data)
            session_data = SessionData(user_id=session_id, **data)
            
            # Check if session is expired (additional check beyond Redis TTL)
            if time.time() - session_data.last_updated > SESSION_TTL:
                logger.info(f"Session expired: {session_id[:20]}...")
                SessionManager.delete_session(session_id)
                return None
            
            return session_data
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Invalid session data for {session_id[:20]}...: {e}")
            SessionManager.delete_session(session_id)
            return None
    
    @staticmethod
    def update_session(session_id: str, session_data: SessionData, ip_address: str = None):
        """
        Update session with new data and refresh TTL.
        
        Args:
            session_id: Session identifier
            session_data: Updated session data
            ip_address: Client IP for tracking updates
        """
        session_data.last_updated = time.time()
        if ip_address and session_data.metadata:
            session_data.metadata["last_activity"] = time.time()
            session_data.metadata["ip_address"] = ip_address
        
        session_key = SessionManager.get_session_key(session_id)
        set_cached_response(session_key, json.dumps(session_data.dict()), ttl=SESSION_TTL)
        
        # Update IP tracking
        if ip_address:
            ip_sessions_key = SessionManager.get_ip_sessions_key(ip_address)
            existing_sessions = get_cached_response(ip_sessions_key)
            if existing_sessions:
                try:
                    sessions_list = json.loads(existing_sessions)
                    for session in sessions_list:
                        if session["session_id"] == session_id:
                            session["last_activity"] = time.time()
                            break
                    set_cached_response(ip_sessions_key, json.dumps(sessions_list), ttl=SESSION_TTL)
                except json.JSONDecodeError:
                    pass
    
    @staticmethod
    def delete_session(session_id: str):
        """Delete a session and clean up tracking."""
        session_key = SessionManager.get_session_key(session_id)
        
        # Get session data to find IP for cleanup
        raw_data = get_cached_response(session_key)
        if raw_data:
            try:
                data = json.loads(raw_data)
                ip_address = data.get("metadata", {}).get("ip_address")
                if ip_address:
                    SessionManager.remove_session_from_ip_tracking(ip_address, session_id)
            except json.JSONDecodeError:
                pass
        
        # Delete the session
        from backend.utils.cache import get_redis_client
        r = get_redis_client()
        r.delete(session_key)
        
        logger.info(f"Deleted session: {session_id[:20]}...")
    
    @staticmethod
    def remove_session_from_ip_tracking(ip_address: str, session_id: str):
        """Remove session from IP tracking list."""
        ip_sessions_key = SessionManager.get_ip_sessions_key(ip_address)
        existing_sessions = get_cached_response(ip_sessions_key)
        
        if existing_sessions:
            try:
                sessions_list = json.loads(existing_sessions)
                sessions_list = [s for s in sessions_list if s["session_id"] != session_id]
                if sessions_list:
                    set_cached_response(ip_sessions_key, json.dumps(sessions_list), ttl=SESSION_TTL)
                else:
                    # Delete empty tracking
                    from backend.utils.cache import get_redis_client
                    r = get_redis_client()
                    r.delete(ip_sessions_key)
            except json.JSONDecodeError:
                pass
    
    @staticmethod
    def cleanup_old_sessions(sessions_list: list):
        """Clean up expired sessions from tracking list."""
        current_time = time.time()
        active_sessions = []
        
        for session in sessions_list:
            if current_time - session.get("last_activity", 0) < SESSION_TTL:
                active_sessions.append(session)
            else:
                # Delete expired session
                SessionManager.delete_session(session["session_id"])
        
        sessions_list.clear()
        sessions_list.extend(active_sessions)
    
    @staticmethod
    def get_session_stats() -> Dict[str, Any]:
        """Get session statistics for monitoring."""
        from backend.utils.cache import get_redis_client
        r = get_redis_client()
        
        # Count active sessions
        session_keys = r.keys("chat_session:*")
        ip_keys = r.keys("ip_sessions:*")
        
        return {
            "active_sessions": len(session_keys),
            "active_ips": len(ip_keys),
            "session_ttl": SESSION_TTL,
            "max_sessions_per_ip": MAX_SESSIONS_PER_IP
        }