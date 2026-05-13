import logging
import time
from typing import Any

from fastapi import FastAPI, Request, Response

from app.core.http_status import HTTPStatusCode
from app.core.request_context import (
    REQUEST_ID_HEADER,
    bind_request_id,
    clear_bound_request_id,
    get_or_create_request_id,
    reset_request_id,
)


async def request_logging_middleware(request: Request, call_next: Any) -> Response:
    logger = logging.getLogger("app.request")
    request_id = get_or_create_request_id(request)
    token = bind_request_id(request, request_id)
    started_at = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
        logger.exception(
            "request_failed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": HTTPStatusCode.INTERNAL_SERVER_ERROR,
                "duration_ms": duration_ms,
                "client": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            },
        )
        raise

    duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
    response.headers[REQUEST_ID_HEADER] = request_id
    logger.info(
        "request_completed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "client": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        },
    )
    reset_request_id(token)
    clear_bound_request_id(request)
    return response


def configure_request_logging(app: FastAPI) -> None:
    app.middleware("http")(request_logging_middleware)
