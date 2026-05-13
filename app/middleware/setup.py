from fastapi import FastAPI

from app.core.config import Settings
from app.middleware.cors import configure_cors
from app.middleware.request_logging import configure_request_logging


def configure_middleware(app: FastAPI, settings: Settings) -> None:
    configure_cors(app, settings)
    configure_request_logging(app)
