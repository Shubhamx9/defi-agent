
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from backend.logging_setup import logger

async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Process request
    response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    logger.info(
        f"{request.client.host} {request.method} {request.url.path} "
        f"Status: {response.status_code} - {process_time:.2f} ms"
    )

    return response
