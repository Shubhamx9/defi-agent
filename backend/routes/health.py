"""
Health check endpoints for monitoring system status.
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from backend.utils.cache import health_check as redis_health
from backend.utils.embedding import health_check as embedding_health
from backend.utils.vector_db import health_check as pinecone_health
from backend.utils.mock_mode import is_mock_mode, get_mode_info
import time
from datetime import datetime

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
def basic_health():
    """Basic health check endpoint."""
    return {
        "status": "ok",
        "message": "DeFi AI backend is running",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@router.get("/detailed")
def detailed_health():
    """Detailed health check for all services."""
    import traceback
    start_time = time.time()

    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "redis": {"status": "unknown", "error": None},
            "embedding_model": {"status": "unknown", "error": None},
            "pinecone": {"status": "unknown", "error": None}
        },
        "response_time_ms": 0
    }

    try:
        # Redis
        from backend.utils import cache
        if redis_health():
            health_status["services"]["redis"]["status"] = "healthy"
        else:
            health_status["services"]["redis"]["status"] = "unhealthy"
            health_status["status"] = "degraded"
    except Exception as e:
        print("❌ Redis health check failed:", e)
        traceback.print_exc()
        health_status["services"]["redis"]["error"] = str(e)
        health_status["status"] = "degraded"

    try:
        if embedding_health():
            health_status["services"]["embedding_model"]["status"] = "healthy"
        else:
            health_status["services"]["embedding_model"]["status"] = "unhealthy"
            health_status["status"] = "degraded"
    except Exception as e:
        print("❌ Embedding model health check failed:", e)
        traceback.print_exc()
        health_status["services"]["embedding_model"]["error"] = str(e)
        health_status["status"] = "degraded"

    try:
        if pinecone_health():
            health_status["services"]["pinecone"]["status"] = "healthy"
        else:
            health_status["services"]["pinecone"]["status"] = "unhealthy"
            health_status["status"] = "degraded"
    except Exception as e:
        print("❌ Pinecone health check failed:", e)
        traceback.print_exc()
        health_status["services"]["pinecone"]["error"] = str(e)
        health_status["status"] = "degraded"

    health_status["response_time_ms"] = round((time.time() - start_time) * 1000, 2)
    return JSONResponse(status_code=200 if health_status["status"] == "healthy" else 503, content=health_status)
