import logging
import os
from dataclasses import dataclass
from functools import lru_cache

LOG_LEVELS = frozenset(logging.getLevelNamesMapping())
TRUE_VALUES = {"1", "true", "yes", "on"}
FALSE_VALUES = {"0", "false", "no", "off"}
MIN_TCP_PORT = 1
MAX_TCP_PORT = 65535


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default

    normalized = value.strip().lower()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False

    raise ValueError(f"{name} must be one of: true, false, 1, 0, yes, no, on, off")


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    return int(value)


def _get_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    return float(value)


def _get_csv(name: str, default: tuple[str, ...] = ()) -> tuple[str, ...]:
    value = os.getenv(name)
    if value is None:
        return default
    return tuple(item.strip() for item in value.split(",") if item.strip())


def _require_non_empty(name: str, value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{name} must not be empty")
    return normalized


def _require_positive_int(name: str, value: int) -> None:
    if value <= 0:
        raise ValueError(f"{name} must be greater than 0")


def _require_non_negative_float(name: str, value: float) -> None:
    if value < 0:
        raise ValueError(f"{name} must be greater than or equal to 0")


def _require_tcp_port(name: str, value: int) -> None:
    if value < MIN_TCP_PORT or value > MAX_TCP_PORT:
        raise ValueError(f"{name} must be between {MIN_TCP_PORT} and {MAX_TCP_PORT}")


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_version: str
    app_env: str
    debug: bool
    docs_enabled: bool
    log_level: str
    cors_origins: tuple[str, ...]
    cors_allow_credentials: bool
    mysql_host: str
    mysql_port: int
    mysql_user: str
    mysql_password: str
    mysql_database: str
    mysql_connect_timeout: int
    mysql_pool_size: int
    mysql_retry_attempts: int
    mysql_retry_delay_seconds: float

    def __post_init__(self) -> None:
        app_env = _require_non_empty("APP_ENV", self.app_env).lower()
        log_level = _require_non_empty("LOG_LEVEL", self.log_level).upper()
        cors_origins = tuple(
            origin.strip() for origin in self.cors_origins if origin.strip()
        )

        if log_level not in LOG_LEVELS:
            allowed = ", ".join(sorted(LOG_LEVELS))
            raise ValueError(f"LOG_LEVEL must be one of: {allowed}")

        if app_env == "production" and self.debug:
            raise ValueError("DEBUG must be false when APP_ENV=production")

        if app_env == "production" and self.docs_enabled:
            raise ValueError("DOCS_ENABLED must be false when APP_ENV=production")

        if self.cors_allow_credentials and "*" in cors_origins:
            raise ValueError(
                "CORS_ORIGINS cannot include * when credentials are enabled"
            )

        _require_tcp_port("MYSQL_PORT", self.mysql_port)
        _require_positive_int("MYSQL_CONNECT_TIMEOUT", self.mysql_connect_timeout)
        _require_positive_int("MYSQL_POOL_SIZE", self.mysql_pool_size)
        _require_positive_int("MYSQL_RETRY_ATTEMPTS", self.mysql_retry_attempts)
        _require_non_negative_float(
            "MYSQL_RETRY_DELAY_SECONDS",
            self.mysql_retry_delay_seconds,
        )

        object.__setattr__(
            self, "app_name", _require_non_empty("APP_NAME", self.app_name)
        )
        object.__setattr__(
            self,
            "app_version",
            _require_non_empty("APP_VERSION", self.app_version),
        )
        object.__setattr__(self, "app_env", app_env)
        object.__setattr__(self, "log_level", log_level)
        object.__setattr__(self, "cors_origins", cors_origins)
        object.__setattr__(
            self,
            "mysql_host",
            _require_non_empty("MYSQL_HOST", self.mysql_host),
        )
        object.__setattr__(
            self,
            "mysql_user",
            _require_non_empty("MYSQL_USER", self.mysql_user),
        )
        object.__setattr__(
            self,
            "mysql_database",
            _require_non_empty("MYSQL_DATABASE", self.mysql_database),
        )

    @classmethod
    def from_env(cls) -> "Settings":
        app_env = os.getenv("APP_ENV", "development").strip().lower()
        is_production = app_env == "production"

        return cls(
            app_name=os.getenv("APP_NAME", "FastAPI Backend Template"),
            app_version=os.getenv("APP_VERSION", "0.1.0"),
            app_env=app_env,
            debug=_get_bool("DEBUG", not is_production),
            docs_enabled=_get_bool("DOCS_ENABLED", not is_production),
            log_level=os.getenv("LOG_LEVEL", "INFO").strip().upper(),
            cors_origins=_get_csv("CORS_ORIGINS"),
            cors_allow_credentials=_get_bool("CORS_ALLOW_CREDENTIALS", False),
            mysql_host=os.getenv("MYSQL_HOST", "127.0.0.1"),
            mysql_port=_get_int("MYSQL_PORT", 3306),
            mysql_user=os.getenv("MYSQL_USER", "root"),
            mysql_password=os.getenv("MYSQL_PASSWORD", ""),
            mysql_database=os.getenv("MYSQL_DATABASE", "fastapi_backend_template"),
            mysql_connect_timeout=_get_int("MYSQL_CONNECT_TIMEOUT", 5),
            mysql_pool_size=_get_int("MYSQL_POOL_SIZE", 5),
            mysql_retry_attempts=_get_int("MYSQL_RETRY_ATTEMPTS", 3),
            mysql_retry_delay_seconds=_get_float("MYSQL_RETRY_DELAY_SECONDS", 0.2),
        )


@lru_cache
def get_settings() -> Settings:
    return Settings.from_env()
