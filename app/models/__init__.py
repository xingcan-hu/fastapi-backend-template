"""Database model definitions."""

from app.models.base import Base
from app.models.demo_user import DemoUser

# Import model modules here so Alembic autogenerate can inspect their metadata.

__all__ = ["Base", "DemoUser"]
