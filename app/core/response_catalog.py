from dataclasses import dataclass
from enum import StrEnum


class ResponseCode(StrEnum):
    SUCCESS = "success"
    INVALID = "invalid"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class ResponseDefinition:
    code: ResponseCode
    message: str


class ResponseCatalog:
    SUCCESS = ResponseDefinition(
        code=ResponseCode.SUCCESS,
        message="Success",
    )
    INVALID_REQUEST = ResponseDefinition(
        code=ResponseCode.INVALID,
        message="Invalid request",
    )
    REQUEST_FAILED = ResponseDefinition(
        code=ResponseCode.FAILED,
        message="Request failed",
    )
