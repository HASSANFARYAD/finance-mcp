from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

class ExpenseCreate(BaseModel):
    date: datetime | None = None
    amount: Decimal
    currency: str = "USD"
    category: str
    description: str | None = None

class ExpenseUpdate(BaseModel):
    status: str | None = None
    amount: Decimal | None = None

class ExpenseOut(BaseModel):
    id: int
    date: datetime
    amount: Decimal
    currency: str
    category: str
    description: str | None
    status: str

    class Config:
        from_attributes = True