from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DemoUserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    display_name: str | None
    is_active: bool
    created_at: datetime
