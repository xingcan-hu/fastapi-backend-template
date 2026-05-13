import asyncio

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import Settings
from app.db.session import get_async_engine


async def check_mysql_ready(settings: Settings) -> str:
    attempts = max(settings.mysql_retry_attempts, 1)
    last_error: SQLAlchemyError | None = None

    for attempt in range(1, attempts + 1):
        try:
            engine = get_async_engine(settings)
            async with engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
            return "ok"
        except SQLAlchemyError as exc:
            last_error = exc
            if attempt == attempts:
                break
            await asyncio.sleep(settings.mysql_retry_delay_seconds)

    if last_error is not None:
        raise last_error

    raise SQLAlchemyError("Failed to connect to MySQL")


async def check_dependencies_ready(settings: Settings) -> dict[str, str]:
    return {"mysql": await check_mysql_ready(settings)}
