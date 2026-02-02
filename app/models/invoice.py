from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Enum, func, Integer
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class InvoiceStatus(enum.Enum):
    draft = "draft"
    sent = "sent"
    paid = "paid"
    cancelled = "cancelled"

class Invoice(BaseModel):
    __tablename__ = "invoices"

    invoice_number = Column(String, unique=True, index=True)
    issue_date = Column(DateTime(timezone=True), server_default=func.now())
    due_date = Column(DateTime(timezone=True))
    client_name = Column(String, nullable=False)
    client_email = Column(String)
    subtotal = Column(Numeric(12, 2), default=0)
    tax_amount = Column(Numeric(12, 2), default=0)
    total = Column(Numeric(12, 2), default=0)
    currency = Column(String, default="USD")
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.draft)
    tax_label = Column(String, nullable=True)
    tax_note = Column(String, nullable=True)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")

class InvoiceItem(BaseModel):
    __abstract__ = False  # needed because no __tablename__ on abstract base sometimes
    __tablename__ = "invoice_items"

    description = Column(String, nullable=False)
    quantity = Column(Numeric(10, 2), default=1)
    unit_price = Column(Numeric(12, 2), nullable=False)
    line_total = Column(Numeric(12, 2), default=0)

    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="invoice_items")
    invoice = relationship("Invoice", back_populates="items")
