from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List
from decimal import Decimal

class InvoiceItemCreate(BaseModel):
    description: str
    quantity: Decimal = 1
    unit_price: Decimal

class InvoiceCreate(BaseModel):
    invoice_number: str
    due_date: datetime
    client_name: str
    client_email: EmailStr | None = None
    currency: str = "USD"
    tax_rate: Decimal | None = None  # optional % for auto calc
    tax_label: str | None = None
    tax_note: str | None = None
    items: List[InvoiceItemCreate]

class InvoiceUpdate(BaseModel):
    status: str | None = None

class InvoiceItemOut(BaseModel):
    id: int
    description: str
    quantity: Decimal
    unit_price: Decimal
    line_total: Decimal

    class Config:
        from_attributes = True

class InvoiceOut(BaseModel):
    id: int
    invoice_number: str
    issue_date: datetime
    due_date: datetime
    client_name: str
    subtotal: Decimal
    tax_amount: Decimal
    total: Decimal
    currency: str
    status: str
    tax_label: str | None = None
    tax_note: str | None = None
    items: List[InvoiceItemOut] = []

    class Config:
        from_attributes = True
