import asyncio

import pytest
from app.api.dependencies import get_db_transaction
from app.db.session import make_mysql_url

from tests.conftest import make_settings


class FakeTransaction:
    def __init__(self, events: list[str]) -> None:
        self._events = events

    async def __aenter__(self) -> "FakeTransaction":
        self._events.append("transaction_enter")
        return self

    async def __aexit__(self, *args: object) -> None:
        self._events.append("transaction_exit")


class FakeSession:
    def __init__(self, events: list[str]) -> None:
        self._events = events

    async def __aenter__(self) -> "FakeSession":
        self._events.append("session_enter")
        return self

    async def __aexit__(self, *args: object) -> None:
        self._events.append("session_exit")

    def begin(self) -> FakeTransaction:
        return FakeTransaction(self._events)


class FakeSessionmaker:
    def __init__(self) -> None:
        self.events: list[str] = []

    def __call__(self) -> FakeSession:
        return FakeSession(self.events)


def test_make_mysql_url_uses_asyncmy_driver_and_existing_settings() -> None:
    settings = make_settings(
        mysql_host="db.example",
        mysql_port=3307,
        mysql_user="app_user",
        mysql_password="secret",
        mysql_database="fastapi_backend_template_test",
    )

    url = make_mysql_url(settings)

    assert url.drivername == "mysql+asyncmy"
    assert url.host == "db.example"
    assert url.port == 3307
    assert url.username == "app_user"
    assert url.password == "secret"
    assert url.database == "fastapi_backend_template_test"
    assert url.query == {"charset": "utf8mb4"}


def test_get_db_transaction_wraps_session_in_transaction(monkeypatch) -> None:
    fake_sessionmaker = FakeSessionmaker()

    def fake_get_async_sessionmaker(_settings: object) -> FakeSessionmaker:
        return fake_sessionmaker

    monkeypatch.setattr(
        "app.api.dependencies.get_async_sessionmaker",
        fake_get_async_sessionmaker,
    )

    async def run_dependency() -> None:
        dependency = get_db_transaction(make_settings())
        session = await anext(dependency)

        assert isinstance(session, FakeSession)
        with pytest.raises(StopAsyncIteration):
            await anext(dependency)

    asyncio.run(run_dependency())

    assert fake_sessionmaker.events == [
        "session_enter",
        "transaction_enter",
        "transaction_exit",
        "session_exit",
    ]
