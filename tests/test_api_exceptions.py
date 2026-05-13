from app.core.exceptions import bad_request_exception, service_unavailable_exception
from app.core.http_status import HTTPStatusCode


def test_bad_request_exception_builds_uniform_detail() -> None:
    exc = bad_request_exception()

    assert exc.status_code == HTTPStatusCode.BAD_REQUEST
    assert exc.detail == {
        "code": "invalid",
        "message": "Invalid request",
    }


def test_service_unavailable_exception_builds_uniform_detail() -> None:
    exc = service_unavailable_exception(dependency="mysql")

    assert exc.status_code == HTTPStatusCode.SERVICE_UNAVAILABLE
    assert exc.detail == {
        "code": "failed",
        "message": "Request failed",
        "dependency": "mysql",
    }
