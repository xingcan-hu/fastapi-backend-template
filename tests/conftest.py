from collections.abc import Iterator

import pytest
from app.core.config import Settings
from app.core.request_context import reset_request_id, set_request_id


def make_settings(**overrides: object) -> Settings:
    values = {
        "app_name": "FastAPI Backend Template",
        "app_version": "0.1.0",
        "app_env": "test",
        "debug": False,
        "docs_enabled": True,
        "log_level": "CRITICAL",
        "cors_origins": (),
        "cors_allow_credentials": False,
        "mysql_host": "127.0.0.1",
        "mysql_port": 3306,
        "mysql_user": "root",
        "mysql_password": "",
        "mysql_database": "fastapi_backend_template",
        "mysql_connect_timeout": 1,
        "mysql_pool_size": 1,
        "mysql_pool_recycle_seconds": 1800,
        "mysql_max_overflow": 0,
        "mysql_pool_timeout": 30,
        "mysql_retry_attempts": 1,
        "mysql_retry_delay_seconds": 0.0,
    }
    values.update(overrides)
    return Settings(**values)


@pytest.fixture(autouse=True)
def reset_request_id_context() -> Iterator[None]:
    token = set_request_id("")
    try:
        yield
    finally:
        reset_request_id(token)
