from pydantic import BaseModel

from app.core.request_context import get_request_id
from app.core.response_catalog import ResponseCatalog, ResponseDefinition


class APIResponse[DataT](BaseModel):
    code: str
    message: str
    data: DataT
    request_id: str


def api_response[DataT](
    data: DataT,
    response: ResponseDefinition = ResponseCatalog.SUCCESS,
) -> APIResponse[DataT]:
    return APIResponse(
        code=response.code.value,
        message=response.message,
        data=data,
        request_id=get_request_id(),
    )
