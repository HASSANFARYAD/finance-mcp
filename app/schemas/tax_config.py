from pydantic import BaseModel
from decimal import Decimal


class TaxConfigCreate(BaseModel):
    name: str
    country: str | None = None
    rate: Decimal
    label: str | None = None
    note: str | None = None


class TaxConfigOut(BaseModel):
    id: int
    name: str
    country: str | None
    rate: Decimal

    class Config:
        from_attributes = True
