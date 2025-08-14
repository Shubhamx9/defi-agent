"""
Health check endpoints for monitoring system status.
"""
from fastapi import APIRouter, HTTPException
from backend.models.schemas import HealthResponse
from backend.utils.cache import health_check as redis_health
from backend.utils.embedding import health_check as embedding_health
from backend.utils.vector_db import health_check as pinecone_health
import time
from typing import Dict, Any

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/", response_model=HealthResponse)
def basic_health():
    """Basic health check endpoint."""
    return HealthResponse(message="DeFi AI backend is running")

@router.get("/detailed")
def detailed_health() -> Dict[str, Any]:
    """Detailed health check for all services."""
    start_time = time.time()
    
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {
            "redis": {"status": "unknown", "error": None},
            "embedding_model": {"status": "unknown", "error": None},
            "pinecone": {"status": "unknown", "error": None}
        },
        "response_time_ms": 0
    }
    
    # Check Redis
    try:
        if redis_health():
            health_status["services"]["redis"]["status"] = "healthy"
        else:
            health_status["services"]["redis"]["status"] = "unhealthy"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["services"]["redis"]["status"] = "unhealthy"
        health_status["services"]["redis"]["error"] = str(e)
        health_status["status"] = "degraded"
    
    # Check Embedding Model
    try:
        if embedding_health():
            health_status["services"]["embedding_model"]["status"] = "healthy"
        else:
            health_status["services"]["embedding_model"]["status"] = "unhealthy"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["services"]["embedding_model"]["status"] = "unhealthy"
        health_status["services"]["embedding_model"]["error"] = str(e)
        health_status["status"] = "degraded"
    
    # Check Pinecone
    try:
        if pinecone_health():
            health_status["services"]["pinecone"]["status"] = "healthy"
        else:
            health_status["services"]["pinecone"]["status"] = "unhealthy"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["services"]["pinecone"]["status"] = "unhealthy"
        health_status["services"]["pinecone"]["error"] = str(e)
        health_status["status"] = "degraded"
    
    # Calculate response time
    health_status["response_time_ms"] = round((time.time() - start_time) * 1000, 2)
    
    # Return appropriate HTTP status
    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status

@router.get("/ready")
def readiness_check():
    """Kubernetes readiness probe endpoint."""
    # Check critical services
    if not redis_health() or not embedding_health() or not pinecone_health():
        raise HTTPException(status_code=503, detail="Service not ready")
    
    return {"status": "ready"}

@router.get("/live")
def liveness_check():
    """Kubernetes liveness probe endpoint."""
    return {"status": "alive"}