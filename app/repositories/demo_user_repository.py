from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.demo_user import DemoUser


class DemoUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_email(self, email: str) -> DemoUser | None:
        statement = select(DemoUser).where(DemoUser.email == email)
        result = await self._session.execute(statement)
        return result.scalar_one_or_none()
