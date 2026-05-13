import pytest
from app.core.config import Settings

from tests.conftest import make_settings


def test_settings_from_env_parses_and_normalizes_values(monkeypatch) -> None:
    monkeypatch.setenv("APP_NAME", " FastAPI Template API ")
    monkeypatch.setenv("APP_VERSION", " 1.2.3 ")
    monkeypatch.setenv("APP_ENV", " TEST ")
    monkeypatch.setenv("DEBUG", "yes")
    monkeypatch.setenv("DOCS_ENABLED", "on")
    monkeypatch.setenv("LOG_LEVEL", "warning")
    monkeypatch.setenv("CORS_ORIGINS", " https://app.example, ,https://admin.example ")
    monkeypatch.setenv("CORS_ALLOW_CREDENTIALS", "true")
    monkeypatch.setenv("MYSQL_HOST", " db.example ")
    monkeypatch.setenv("MYSQL_PORT", "3307")
    monkeypatch.setenv("MYSQL_USER", " app_user ")
    monkeypatch.setenv("MYSQL_PASSWORD", "secret")
    monkeypatch.setenv("MYSQL_DATABASE", " fastapi_backend_template_test ")
    monkeypatch.setenv("MYSQL_CONNECT_TIMEOUT", "10")
    monkeypatch.setenv("MYSQL_POOL_SIZE", "3")
    monkeypatch.setenv("MYSQL_POOL_RECYCLE_SECONDS", "1200")
    monkeypatch.setenv("MYSQL_MAX_OVERFLOW", "7")
    monkeypatch.setenv("MYSQL_POOL_TIMEOUT", "15")
    monkeypatch.setenv("MYSQL_RETRY_ATTEMPTS", "2")
    monkeypatch.setenv("MYSQL_RETRY_DELAY_SECONDS", "0.5")

    settings = Settings.from_env()

    assert settings.app_name == "FastAPI Template API"
    assert settings.app_version == "1.2.3"
    assert settings.app_env == "test"
    assert settings.debug is True
    assert settings.docs_enabled is True
    assert settings.log_level == "WARNING"
    assert settings.cors_origins == ("https://app.example", "https://admin.example")
    assert settings.cors_allow_credentials is True
    assert settings.mysql_host == "db.example"
    assert settings.mysql_port == 3307
    assert settings.mysql_user == "app_user"
    assert settings.mysql_password == "secret"
    assert settings.mysql_database == "fastapi_backend_template_test"
    assert settings.mysql_connect_timeout == 10
    assert settings.mysql_pool_size == 3
    assert settings.mysql_pool_recycle_seconds == 1200
    assert settings.mysql_max_overflow == 7
    assert settings.mysql_pool_timeout == 15
    assert settings.mysql_retry_attempts == 2
    assert settings.mysql_retry_delay_seconds == 0.5


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"log_level": "LOUD"}, "LOG_LEVEL"),
        ({"mysql_port": 0}, "MYSQL_PORT"),
        ({"mysql_connect_timeout": 0}, "MYSQL_CONNECT_TIMEOUT"),
        ({"mysql_pool_size": 0}, "MYSQL_POOL_SIZE"),
        ({"mysql_pool_recycle_seconds": 0}, "MYSQL_POOL_RECYCLE_SECONDS"),
        ({"mysql_max_overflow": -1}, "MYSQL_MAX_OVERFLOW"),
        ({"mysql_pool_timeout": 0}, "MYSQL_POOL_TIMEOUT"),
        ({"mysql_retry_attempts": 0}, "MYSQL_RETRY_ATTEMPTS"),
        ({"mysql_retry_delay_seconds": -0.1}, "MYSQL_RETRY_DELAY_SECONDS"),
        ({"mysql_host": " "}, "MYSQL_HOST"),
        ({"mysql_user": " "}, "MYSQL_USER"),
        ({"mysql_database": " "}, "MYSQL_DATABASE"),
    ],
)
def test_settings_rejects_invalid_values(overrides, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        make_settings(**overrides)


def test_settings_rejects_production_debug() -> None:
    with pytest.raises(ValueError, match="DEBUG"):
        make_settings(app_env="production", debug=True, docs_enabled=False)


def test_settings_rejects_production_docs() -> None:
    with pytest.raises(ValueError, match="DOCS_ENABLED"):
        make_settings(app_env="production", debug=False, docs_enabled=True)


def test_settings_rejects_wildcard_cors_with_credentials() -> None:
    with pytest.raises(ValueError, match="CORS_ORIGINS"):
        make_settings(cors_origins=("*",), cors_allow_credentials=True)
