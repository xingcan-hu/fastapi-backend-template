import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

from app.core.request_context import get_request_id

RESERVED_LOG_ATTRS = set(logging.makeLogRecord({}).__dict__)
TEMPLATE_LOG_HANDLER_ATTR = "_fastapi_backend_template_json_handler"


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        request_id = get_request_id()
        if request_id:
            payload["request_id"] = request_id

        for key, value in record.__dict__.items():
            if key not in RESERVED_LOG_ATTRS and key not in payload:
                payload[key] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False, default=str)


def configure_logging(level: str) -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    for handler in root_logger.handlers:
        if getattr(handler, TEMPLATE_LOG_HANDLER_ATTR, False):
            handler.setLevel(level)
            handler.setFormatter(JsonFormatter())
            break
    else:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        handler.setFormatter(JsonFormatter())
        setattr(handler, TEMPLATE_LOG_HANDLER_ATTR, True)
        root_logger.addHandler(handler)

    logging.getLogger("uvicorn.access").disabled = True
