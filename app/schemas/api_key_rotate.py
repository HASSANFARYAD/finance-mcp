from pydantic import BaseModel


class ApiKeyRotate(BaseModel):
    ttl_days: int | None = None
    name: str | None = None  # optional new name
