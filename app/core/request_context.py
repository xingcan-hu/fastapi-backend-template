import contextvars
import re
import uuid

from fastapi import Request

REQUEST_ID_HEADER = "X-Request-ID"
REQUEST_ID_CONTEXT_TOKEN_STATE_KEY = "_request_id_context_token"
REQUEST_ID_MAX_LENGTH = 128
REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]+$")
request_id_context: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id",
    default="",
)


def get_request_id() -> str:
    return request_id_context.get()


def set_request_id(request_id: str) -> contextvars.Token[str]:
    return request_id_context.set(request_id)


def reset_request_id(token: contextvars.Token[str]) -> None:
    request_id_context.reset(token)


def bind_request_id(request: Request, request_id: str) -> contextvars.Token[str]:
    token = set_request_id(request_id)
    setattr(request.state, REQUEST_ID_CONTEXT_TOKEN_STATE_KEY, token)
    return token


def clear_bound_request_id(request: Request) -> None:
    setattr(request.state, REQUEST_ID_CONTEXT_TOKEN_STATE_KEY, None)


def reset_bound_request_id(request: Request) -> None:
    token = getattr(request.state, REQUEST_ID_CONTEXT_TOKEN_STATE_KEY, None)
    if token is None:
        return

    reset_request_id(token)
    clear_bound_request_id(request)


def is_valid_request_id(request_id: str) -> bool:
    return (
        0 < len(request_id) <= REQUEST_ID_MAX_LENGTH
        and REQUEST_ID_PATTERN.fullmatch(request_id) is not None
    )


def get_or_create_request_id(request: Request) -> str:
    request_id = request.headers.get(REQUEST_ID_HEADER)
    if request_id is not None:
        normalized_request_id = request_id.strip()
        if is_valid_request_id(normalized_request_id):
            return normalized_request_id

    return str(uuid.uuid4())
