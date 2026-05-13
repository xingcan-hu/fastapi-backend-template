from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import Settings, get_settings

AsyncSessionMaker = async_sessionmaker[AsyncSession]

_engine: AsyncEngine | None = None
_engine_settings: Settings | None = None
_sessionmaker: AsyncSessionMaker | None = None


def make_mysql_url(settings: Settings) -> URL:
    return URL.create(
        drivername="mysql+asyncmy",
        username=settings.mysql_user,
        password=settings.mysql_password,
        host=settings.mysql_host,
        port=settings.mysql_port,
        database=settings.mysql_database,
        query={"charset": "utf8mb4"},
    )


def get_async_engine(settings: Settings | None = None) -> AsyncEngine:
    global _engine, _engine_settings

    settings = settings or get_settings()
    if _engine is not None and _engine_settings == settings:
        return _engine

    _engine = create_async_engine(
        make_mysql_url(settings),
        connect_args={"connect_timeout": settings.mysql_connect_timeout},
        pool_pre_ping=True,
        pool_size=settings.mysql_pool_size,
    )
    _engine_settings = settings
    return _engine


def get_async_sessionmaker(settings: Settings | None = None) -> AsyncSessionMaker:
    global _sessionmaker

    engine = get_async_engine(settings)
    if _sessionmaker is None or _sessionmaker.kw["bind"] is not engine:
        _sessionmaker = async_sessionmaker(
            bind=engine,
            expire_on_commit=False,
        )
    return _sessionmaker


async def dispose_async_engine() -> None:
    global _engine, _engine_settings, _sessionmaker

    if _engine is not None:
        await _engine.dispose()

    _engine = None
    _engine_settings = None
    _sessionmaker = None
