from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.db.session import get_async_sessionmaker


def get_app_settings(request: Request) -> Settings:
    return request.app.state.settings


async def get_db_session(
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> AsyncGenerator[AsyncSession]:
    sessionmaker = get_async_sessionmaker(settings)
    async with sessionmaker() as session:
        yield session
