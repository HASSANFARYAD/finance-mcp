from sqlalchemy import Column, String, Integer, DateTime, func
from sqlalchemy.orm import relationship
from passlib.context import CryptContext
from .base import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    invoices = relationship("Invoice", back_populates="owner", cascade="all, delete-orphan")
    invoice_items = relationship("InvoiceItem", back_populates="owner", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="owner", cascade="all, delete-orphan")
    api_keys = relationship("ApiKey", back_populates="owner", cascade="all, delete-orphan")
    tax_configs = relationship("TaxConfig", back_populates="owner", cascade="all, delete-orphan")
    company_profile = relationship("CompanyProfile", back_populates="owner", uselist=False, cascade="all, delete-orphan")

    def verify_password(self, plain_password):
        return pwd_context.verify(plain_password, self.hashed_password)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)
