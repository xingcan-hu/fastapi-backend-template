import logging

from app.core.logger import TEMPLATE_LOG_HANDLER_ATTR, configure_logging


def test_configure_logging_preserves_existing_handlers_and_is_idempotent() -> None:
    root_logger = logging.getLogger()
    original_handlers = list(root_logger.handlers)
    original_level = root_logger.level
    existing_handler = logging.NullHandler()

    try:
        root_logger.handlers = [existing_handler]

        configure_logging("INFO")
        configure_logging("DEBUG")

        template_handlers = [
            handler
            for handler in root_logger.handlers
            if getattr(handler, TEMPLATE_LOG_HANDLER_ATTR, False)
        ]

        assert existing_handler in root_logger.handlers
        assert len(template_handlers) == 1
        assert root_logger.level == logging.DEBUG
    finally:
        root_logger.handlers = original_handlers
        root_logger.setLevel(original_level)
