from pydantic import BaseModel


class RootRead(BaseModel):
    message: str
