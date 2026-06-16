import time
from fastapi import Request

from app.utils.logger import logger


async def app_middleware(
    request: Request,
    call_next
):
    start_time = time.time()

    response = await call_next(request)

    process_time = (
        time.time() - start_time
    )

    logger.info(
        f"Request Method: {request.method}, "
        f"Request URL: {request.url}, "
        f"Process Time: {process_time:.4f} seconds."
    )

    # Security Headers
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = (
        "strict-origin-when-cross-origin"
    )
    response.headers["Cache-Control"] = "no-store"

    # Request performance
    response.headers["X-Process-Time"] = (
        f"{process_time:.4f}"
    )

    return response