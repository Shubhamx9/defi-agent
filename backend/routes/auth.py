# backend/routes/auth.py
import uuid
from fastapi import APIRouter, Request, Response, HTTPException
from slowapi.util import get_remote_address
from backend.config.settings import security_settings
from backend.utils.session_manager import SessionManager
from backend.logging_setup import logger

router = APIRouter()

# Cookie settings — allow HTTP in DEBUG to make local dev easy
COOKIE_COMMON = {
    "httponly": True,
    "secure": False if getattr(security_settings, "DEBUG", False) else True,
    "samesite": "lax",
    "max_age": 3600,
}


@router.post("/login")
def login(request: Request, response: Response):
    """
    Temporary/dev login: returns a random user_id and creates a session for it.
    Replace with real auth later.
    """
    try:
        # Generate a short random user id for dev use
        user_id = f"devuser-{uuid.uuid4().hex[:8]}"
        client_ip = get_remote_address(request)
        user_agent = request.headers.get("user-agent", "unknown")

        # Create initial session for the generated user_id
        session_id = SessionManager.create_new_session(user_id, client_ip, user_agent)

        # Set cookies so subsequent requests authenticate automatically
        response.set_cookie(key="user_id", value=user_id, **COOKIE_COMMON)
        response.set_cookie(key="session_id", value=session_id, **COOKIE_COMMON)

        logger.info(f"[dev-login] created user {user_id} session {session_id[:20]} for IP {client_ip}")
        # Return user_id and session_id in response for non-frontend clients
        return {"message": "dev login successful", "user_id": user_id, "session_id": session_id}

    except ValueError as ve:
        # e.g., per-user session limit (unlikely for random dev users)
        logger.exception("Failed to create session during dev login: %s", ve)
        raise HTTPException(status_code=429, detail=str(ve))
    except Exception as e:
        logger.exception("Unexpected error in dev login: %s", e)
        raise HTTPException(status_code=500, detail="Could not create dev session")


@router.post("/logout")
def logout(request: Request, response: Response):
    """
    Clear cookies and delete session if present.
    """
    user_id = request.cookies.get("user_id")
    session_id = request.cookies.get("session_id")
    if user_id and session_id:
        try:
            SessionManager.delete_session(user_id, session_id)
        except Exception:
            logger.exception("Failed to delete session during logout for user %s", user_id)

    response.delete_cookie("user_id")
    response.delete_cookie("session_id")
    return {"message": "logged out (dev)"}
