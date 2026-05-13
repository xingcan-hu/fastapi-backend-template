from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.exc import SQLAlchemyError

from app.api.dependencies import get_app_settings
from app.core.config import Settings
from app.core.exceptions import service_unavailable_exception
from app.services.health import check_dependencies_ready

router = APIRouter(tags=["health"])


@router.get("/health", include_in_schema=False)
def health_check() -> dict[str, str]:
    return health_live()


@router.get("/health/live", summary="Liveness check")
def health_live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready", summary="Readiness check")
async def health_ready(
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> dict[str, object]:
    try:
        dependencies = await check_dependencies_ready(settings)
    except SQLAlchemyError as exc:
        raise service_unavailable_exception(
            dependency="mysql",
            reason=exc.__class__.__name__,
        ) from exc

    return {"status": "ok", "dependencies": dependencies}
