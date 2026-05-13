from typing import Any

from fastapi import HTTPException

from app.core.http_status import HTTPStatusCode
from app.core.response_catalog import ResponseCatalog, ResponseDefinition


class APIException(HTTPException):
    def __init__(
        self,
        status_code: HTTPStatusCode,
        response: ResponseDefinition,
        **details: Any,
    ) -> None:
        detail = {
            "code": response.code.value,
            "message": response.message,
        }
        detail.update(
            {
                key: value
                for key, value in details.items()
                if key not in {"code", "message"}
            },
        )
        super().__init__(status_code=status_code, detail=detail)


def api_exception(
    status_code: HTTPStatusCode,
    response: ResponseDefinition,
    **details: Any,
) -> APIException:
    return APIException(
        status_code=status_code,
        response=response,
        **details,
    )


def bad_request_exception(
    **details: Any,
) -> APIException:
    return api_exception(
        status_code=HTTPStatusCode.BAD_REQUEST,
        response=ResponseCatalog.INVALID_REQUEST,
        **details,
    )


def invalid_exception(
    status_code: HTTPStatusCode = HTTPStatusCode.BAD_REQUEST,
    **details: Any,
) -> APIException:
    return api_exception(
        status_code=status_code,
        response=ResponseCatalog.INVALID_REQUEST,
        **details,
    )


def failed_exception(
    status_code: HTTPStatusCode = HTTPStatusCode.INTERNAL_SERVER_ERROR,
    **details: Any,
) -> APIException:
    return api_exception(
        status_code=status_code,
        response=ResponseCatalog.REQUEST_FAILED,
        **details,
    )


def service_unavailable_exception(
    **details: Any,
) -> APIException:
    return failed_exception(
        status_code=HTTPStatusCode.SERVICE_UNAVAILABLE,
        **details,
    )
