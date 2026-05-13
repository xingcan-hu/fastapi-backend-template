import logging
from typing import Any, cast

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.types import ExceptionHandler

from app.core.http_status import HTTPStatusCode
from app.core.request_context import (
    REQUEST_ID_HEADER,
    get_request_id,
    reset_bound_request_id,
)
from app.core.response_catalog import ResponseCatalog


def build_response_payload(
    code: str,
    message: str,
    details: Any | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "code": code,
        "message": message,
        "request_id": get_request_id(),
    }

    if details is not None:
        payload["details"] = details

    return payload


def _error_headers() -> dict[str, str]:
    request_id = get_request_id()
    if not request_id:
        return {}
    return {REQUEST_ID_HEADER: request_id}


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    detail = exc.detail
    response = (
        ResponseCatalog.REQUEST_FAILED
        if exc.status_code >= HTTPStatusCode.INTERNAL_SERVER_ERROR
        else ResponseCatalog.INVALID_REQUEST
    )
    details = None

    if isinstance(detail, dict):
        code = str(detail.get("code", response.code.value))
        message = str(detail.get("message", response.message))
        extra_details = {
            key: value
            for key, value in detail.items()
            if key not in {"code", "message"}
        }
        details = extra_details or None
    else:
        code = response.code.value
        message = response.message

    if exc.status_code >= HTTPStatusCode.INTERNAL_SERVER_ERROR:
        logging.getLogger("app.error").error(
            "http_exception",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": exc.status_code,
                "error_code": code,
            },
        )

    return JSONResponse(
        status_code=exc.status_code,
        content=build_response_payload(code, message, details),
        headers=_error_headers(),
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    logging.getLogger("app.error").warning(
        ResponseCatalog.INVALID_REQUEST.code.value,
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": HTTPStatusCode.UNPROCESSABLE_ENTITY,
        },
    )
    return JSONResponse(
        status_code=HTTPStatusCode.UNPROCESSABLE_ENTITY,
        content=build_response_payload(
            code=ResponseCatalog.INVALID_REQUEST.code.value,
            message=ResponseCatalog.INVALID_REQUEST.message,
            details=exc.errors(),
        ),
        headers=_error_headers(),
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logging.getLogger("app.error").exception(
        "unhandled_exception",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": HTTPStatusCode.INTERNAL_SERVER_ERROR,
        },
    )
    response = JSONResponse(
        status_code=HTTPStatusCode.INTERNAL_SERVER_ERROR,
        content=build_response_payload(
            code=ResponseCatalog.REQUEST_FAILED.code.value,
            message=ResponseCatalog.REQUEST_FAILED.message,
        ),
        headers=_error_headers(),
    )
    reset_bound_request_id(request)
    return response


def configure_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        StarletteHTTPException,
        cast(ExceptionHandler, http_exception_handler),
    )
    app.add_exception_handler(
        RequestValidationError,
        cast(ExceptionHandler, validation_exception_handler),
    )
    app.add_exception_handler(Exception, unhandled_exception_handler)
