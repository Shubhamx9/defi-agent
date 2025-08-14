"""
Global exception handler with structured error responses.
"""
import logging
import traceback
import uuid
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from backend.models.schemas import ErrorResponse, ErrorDetail
from backend.config.settings import settings

logger = logging.getLogger(__name__)

async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions with structured responses."""
    
    # Generate unique request ID for tracking
    request_id = str(uuid.uuid4())
    
    # Log the full exception with context
    logger.exception(
        f"Unhandled exception [Request ID: {request_id}] "
        f"Path: {request.url.path} "
        f"Method: {request.method} "
        f"Error: {exc}"
    )
    
    # Handle different exception types
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP Exception",
                "details": [ErrorDetail(code=str(exc.status_code), message=exc.detail)],
                "request_id": request_id
            }
        )
    
    # Handle validation errors
    if hasattr(exc, 'errors'):  # Pydantic validation errors
        error_details = []
        for error in exc.errors():
            error_details.append(ErrorDetail(
                code="validation_error",
                message=error.get('msg', 'Validation failed'),
                field='.'.join(str(loc) for loc in error.get('loc', []))
            ))
        
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation Error",
                "details": error_details,
                "request_id": request_id
            }
        )
    
    # Handle rate limiting errors
    if "rate limit" in str(exc).lower():
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate Limit Exceeded",
                "details": [ErrorDetail(code="rate_limit", message="Too many requests")],
                "request_id": request_id
            }
        )
    
    # Generic server error
    error_message = str(exc) if settings.DEBUG else "An internal server error occurred"
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "details": [ErrorDetail(code="internal_error", message=error_message)],
            "request_id": request_id,
            "timestamp": __import__('time').time()
        }
    )
