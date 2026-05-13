from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_app_settings
from app.core.config import Settings
from app.schemas.api_response import APIResponse, api_response
from app.schemas.system import RootRead

router = APIRouter(tags=["system"])


@router.get("/", response_model=APIResponse[RootRead])
def read_root(
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> APIResponse[RootRead]:
    return api_response(RootRead(message=settings.app_name))
