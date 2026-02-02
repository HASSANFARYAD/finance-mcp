from pydantic import BaseModel
from datetime import datetime

class ApiKeyCreate(BaseModel):
    name: str | None = None
    ttl_days: int | None = None

class ApiKeyOut(BaseModel):
    id: int
    name: str | None
    created_at: datetime
    expires_at: datetime | None = None
    last_used_at: datetime | None = None

    class Config:
        from_attributes = True

class ApiKeyFullOut(ApiKeyOut):
    plain_key: str  # only on creation
