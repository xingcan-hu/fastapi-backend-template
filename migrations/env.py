from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from app.core.config import Settings
from app.db.session import make_mysql_url
from app.models import Base
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _settings() -> Settings:
    return Settings.from_env()


def _database_url(settings: Settings) -> str:
    return make_mysql_url(settings).render_as_string(hide_password=False)


def run_migrations_offline() -> None:
    settings = _settings()
    context.configure(
        url=_database_url(settings),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    settings = _settings()
    connectable = create_async_engine(
        make_mysql_url(settings),
        connect_args={"connect_timeout": settings.mysql_connect_timeout},
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
