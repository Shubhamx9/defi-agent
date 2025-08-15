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

@router.get("/sessions")
def session_stats():
    """Get session statistics for monitoring."""
    from backend.utils.session_manager import SessionManager
    return SessionManager.get_session_stats()

@router.get("/models")
def model_status():
    """Check status of AI models and get recommendations."""
    from backend.utils.model_selector import (
        get_model_info, 
        recommend_model_for_task, 
        get_upgrade_info,
        is_model_available,
        get_current_system_info,
        calculate_cost_savings
    )
    from backend.config.settings import settings
    
    current_models = {
        "intent": settings.INTENT_MODEL,
        "query": settings.QUERY_MODEL,
        "action": settings.ACTION_MODEL
    }
    
    model_status = {}
    for task, model in current_models.items():
        model_status[task] = {
            "current_model": model,
            "available": "not_tested",  # Don't test availability to avoid API calls
            "info": get_model_info(model),
            "recommended_cost": recommend_model_for_task(task, "cost"),
            "recommended_speed": recommend_model_for_task(task, "speed"),
            "recommended_capability": recommend_model_for_task(task, "capability")
        }
    
    # Get current system info and analysis
    system_info = get_current_system_info()
    upgrade_status = get_upgrade_info()
    cost_analysis = calculate_cost_savings()
    
    return {
        "current_system": system_info,
        "current_models": model_status,
        "system_available": upgrade_status["available"],
        "cost_analysis": cost_analysis,
        "recommended_config": upgrade_status["recommended_config"],
        "upgrade_benefits": upgrade_status["upgrade_instructions"]
    }