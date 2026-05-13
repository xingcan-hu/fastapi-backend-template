from app.core.exceptions import bad_request_exception
from app.core.http_status import HTTPStatusCode
from app.main import create_app
from fastapi.testclient import TestClient
from sqlalchemy import TextClause
from sqlalchemy.exc import SQLAlchemyError

from tests.conftest import make_settings


def test_root_returns_uniform_success_shape() -> None:
    client = TestClient(create_app(make_settings()))

    response = client.get("/", headers={"X-Request-ID": "root-request"})

    assert response.status_code == HTTPStatusCode.OK
    assert response.json() == {
        "code": "success",
        "message": "Success",
        "data": {
            "message": "FastAPI Backend Template",
        },
        "request_id": "root-request",
    }
    assert response.headers["X-Request-ID"] == "root-request"


def test_docs_are_available_when_enabled() -> None:
    client = TestClient(create_app(make_settings(docs_enabled=True)))

    docs_response = client.get("/docs")
    openapi_response = client.get("/openapi.json")

    assert docs_response.status_code == HTTPStatusCode.OK
    assert openapi_response.status_code == HTTPStatusCode.OK
    assert openapi_response.json()["info"]["title"] == "FastAPI Backend Template"


def test_docs_are_hidden_when_disabled() -> None:
    client = TestClient(create_app(make_settings(docs_enabled=False)))

    assert client.get("/docs").status_code == HTTPStatusCode.NOT_FOUND
    assert client.get("/openapi.json").status_code == HTTPStatusCode.NOT_FOUND


def test_liveness_returns_request_id_header() -> None:
    client = TestClient(create_app(make_settings()))

    response = client.get("/health/live", headers={"X-Request-ID": "test-request-id"})

    assert response.status_code == HTTPStatusCode.OK
    assert response.json() == {"status": "ok"}
    assert response.headers["X-Request-ID"] == "test-request-id"


def test_not_found_uses_uniform_error_shape() -> None:
    client = TestClient(create_app(make_settings()))

    response = client.get("/missing", headers={"X-Request-ID": "missing-request"})

    assert response.status_code == HTTPStatusCode.NOT_FOUND
    assert response.json() == {
        "code": "invalid",
        "message": "Invalid request",
        "request_id": "missing-request",
    }
    assert response.headers["X-Request-ID"] == "missing-request"


def test_unhandled_exception_uses_uniform_error_shape() -> None:
    app = create_app(make_settings())

    @app.get("/boom")
    def boom() -> None:
        raise RuntimeError("boom")

    client = TestClient(app, raise_server_exceptions=False)

    response = client.get("/boom", headers={"X-Request-ID": "boom-request"})

    assert response.status_code == HTTPStatusCode.INTERNAL_SERVER_ERROR
    assert response.json() == {
        "code": "failed",
        "message": "Request failed",
        "request_id": "boom-request",
    }
    assert response.headers["X-Request-ID"] == "boom-request"


def test_api_exception_without_details_omits_empty_details() -> None:
    app = create_app(make_settings())

    @app.get("/bad-request")
    def bad_request() -> None:
        raise bad_request_exception()

    client = TestClient(app)

    response = client.get(
        "/bad-request",
        headers={"X-Request-ID": "bad-request"},
    )

    assert response.status_code == HTTPStatusCode.BAD_REQUEST
    assert response.json() == {
        "code": "invalid",
        "message": "Invalid request",
        "request_id": "bad-request",
    }


def test_validation_exception_uses_invalid_code() -> None:
    client = TestClient(create_app(make_settings()))

    response = client.get(
        "/demo/users",
        params={"email": "x"},
        headers={"X-Request-ID": "validation-request"},
    )

    assert response.status_code == HTTPStatusCode.UNPROCESSABLE_ENTITY
    body = response.json()
    assert body["code"] == "invalid"
    assert body["message"] == "Invalid request"
    assert body["request_id"] == "validation-request"
    assert body["details"][0]["loc"] == ["query", "email"]


def test_cors_allows_configured_origin_only() -> None:
    client = TestClient(
        create_app(
            make_settings(
                cors_origins=("https://app.example",),
            ),
        ),
    )

    allowed_response = client.options(
        "/health/live",
        headers={
            "Origin": "https://app.example",
            "Access-Control-Request-Method": "GET",
        },
    )
    blocked_response = client.options(
        "/health/live",
        headers={
            "Origin": "https://evil.example",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert allowed_response.status_code == HTTPStatusCode.OK
    assert (
        allowed_response.headers["access-control-allow-origin"] == "https://app.example"
    )
    assert "access-control-allow-origin" not in blocked_response.headers


def test_readiness_returns_ok_when_mysql_query_succeeds(monkeypatch) -> None:
    class FakeConnection:
        async def __aenter__(self) -> "FakeConnection":
            return self

        async def __aexit__(self, *args: object) -> None:
            return None

        async def execute(self, statement: TextClause) -> None:
            assert str(statement) == "SELECT 1"

    class FakeEngine:
        def connect(self) -> FakeConnection:
            return FakeConnection()

    def fake_get_async_engine(settings):
        return FakeEngine()

    monkeypatch.setattr(
        "app.services.health.get_async_engine",
        fake_get_async_engine,
    )
    client = TestClient(create_app(make_settings()))

    response = client.get("/health/ready")

    assert response.status_code == HTTPStatusCode.OK
    assert response.json() == {"status": "ok", "dependencies": {"mysql": "ok"}}


def test_readiness_returns_uniform_error_when_mysql_fails(monkeypatch) -> None:
    class FakeEngine:
        def connect(self) -> None:
            raise SQLAlchemyError("database unavailable")

    def fake_get_async_engine(settings):
        return FakeEngine()

    monkeypatch.setattr(
        "app.services.health.get_async_engine",
        fake_get_async_engine,
    )
    client = TestClient(create_app(make_settings()))

    response = client.get("/health/ready", headers={"X-Request-ID": "ready-request"})

    assert response.status_code == HTTPStatusCode.SERVICE_UNAVAILABLE
    assert response.json() == {
        "code": "failed",
        "message": "Request failed",
        "details": {
            "dependency": "mysql",
            "reason": "SQLAlchemyError",
        },
        "request_id": "ready-request",
    }
