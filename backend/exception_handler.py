
# exception_handler.py
import uuid
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from backend.models.schemas import ErrorDetail
from backend.logging_setup import logger  # use the rotating logger

async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions with structured responses."""
    request_id = str(uuid.uuid4())

    # Log full traceback
    logger.exception(f"Unhandled exception [Request ID: {request_id}] "
                     f"Path: {request.url.path} Method: {request.method} Error: {exc}")

    # HTTP exceptions
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP Exception",
                "details": [ErrorDetail(code=str(exc.status_code), message=exc.detail)],
                "request_id": request_id
            }
        )

    # Validation errors
    if hasattr(exc, 'errors'):
        error_details = [
            ErrorDetail(
                code="validation_error",
                message=e.get('msg', 'Validation failed'),
                field='.'.join(str(loc) for loc in e.get('loc', []))
            ) for e in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content={"error": "Validation Error", "details": error_details, "request_id": request_id}
        )

    # Rate limit error detection
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
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "details": [ErrorDetail(code="internal_error", message="An internal server error occurred")],
            "request_id": request_id
        }
    )
