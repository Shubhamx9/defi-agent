import time
import logging
from fastapi import Request

logger = logging.getLogger(__name__)

async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Read request body safely
    try:
        body_bytes = await request.body()
        body_text = body_bytes.decode("utf-8") if body_bytes else ""
    except Exception:
        body_text = "<Could not read body>"

    logger.info(
        f"⬅️ Incoming Request | {request.method} {request.url.path} | "
        f"Query: {request.url.query or 'None'} | Body: {body_text}"
    )

    # Process request
    response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    logger.info(
        f"➡️ Outgoing Response | {request.method} {request.url.path} | "
        f"Status: {response.status_code} | Time: {process_time:.2f}ms"
    )

    return response
