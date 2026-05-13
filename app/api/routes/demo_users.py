from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db_session
from app.repositories.demo_user_repository import DemoUserRepository
from app.schemas.api_response import APIResponse, api_response
from app.schemas.demo_user import DemoUserRead

router = APIRouter(prefix="/demo/users", tags=["demo-users"])


@router.get(
    "",
    response_model=APIResponse[DemoUserRead | None],
    summary="Find demo user by email",
)
async def read_demo_user_by_email(
    email: Annotated[str, Query(min_length=3, max_length=254)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> APIResponse[DemoUserRead | None]:
    normalized_email = email.strip()
    demo_user = await DemoUserRepository(session).get_by_email(normalized_email)

    if demo_user is None:
        return api_response(None)

    return api_response(DemoUserRead.model_validate(demo_user))
