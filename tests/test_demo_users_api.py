from collections.abc import AsyncGenerator
from datetime import datetime
from types import SimpleNamespace

from app.api.dependencies import get_db_session
from app.core.http_status import HTTPStatusCode
from app.main import create_app
from app.repositories.demo_user_repository import DemoUserRepository
from fastapi.testclient import TestClient

from tests.conftest import make_settings


async def fake_get_db_session() -> AsyncGenerator[object]:
    yield object()


def test_get_demo_user_by_email_returns_user(monkeypatch) -> None:
    async def fake_get_by_email(self, email: str):
        assert email == "ada@example.com"
        return SimpleNamespace(
            id=1,
            email="ada@example.com",
            display_name="Ada Lovelace",
            is_active=True,
            created_at=datetime(2026, 5, 13, 1, 2, 3),
        )

    monkeypatch.setattr(DemoUserRepository, "get_by_email", fake_get_by_email)
    app = create_app(make_settings())
    app.dependency_overrides[get_db_session] = fake_get_db_session
    client = TestClient(app)

    response = client.get(
        "/demo/users",
        params={"email": " ada@example.com "},
        headers={"X-Request-ID": "demo-user-ok-request"},
    )

    assert response.status_code == HTTPStatusCode.OK
    assert response.json() == {
        "code": "success",
        "message": "Success",
        "data": {
            "id": 1,
            "email": "ada@example.com",
            "display_name": "Ada Lovelace",
            "is_active": True,
            "created_at": "2026-05-13T01:02:03",
        },
        "request_id": "demo-user-ok-request",
    }


def test_get_demo_user_by_email_returns_success_with_null_data_when_missing(
    monkeypatch,
) -> None:
    async def fake_get_by_email(self, email: str):
        assert email == "missing@example.com"
        return None

    monkeypatch.setattr(DemoUserRepository, "get_by_email", fake_get_by_email)
    app = create_app(make_settings())
    app.dependency_overrides[get_db_session] = fake_get_db_session
    client = TestClient(app)

    response = client.get(
        "/demo/users",
        params={"email": "missing@example.com"},
        headers={"X-Request-ID": "demo-user-request"},
    )

    assert response.status_code == HTTPStatusCode.OK
    assert response.json() == {
        "code": "success",
        "message": "Success",
        "data": None,
        "request_id": "demo-user-request",
    }
