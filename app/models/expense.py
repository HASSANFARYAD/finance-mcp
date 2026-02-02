from sqlalchemy import Column, String, DateTime, Numeric, Enum, Integer, ForeignKey, func
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class ExpenseStatus(enum.Enum):
    pending = "pending"
    approved = "approved"
    reimbursed = "reimbursed"

class Expense(BaseModel):
    __tablename__ = "expenses"

    date = Column(DateTime(timezone=True), server_default=func.now())
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String, default="USD")
    category = Column(String, nullable=False)  # e.g., Travel, Office Supplies
    description = Column(String)
    receipt_url = Column(String)  # file upload path / URL
    status = Column(Enum(ExpenseStatus), default=ExpenseStatus.pending)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="expenses")
