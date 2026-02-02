from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class TaxConfig(BaseModel):
    __tablename__ = "tax_configs"

    name = Column(String, nullable=False)          # e.g., "Standard VAT"
    country = Column(String, nullable=True)        # optional country code
    rate = Column(Numeric(6, 3), nullable=False)   # percentage
    label = Column(String, nullable=True)
    note = Column(String, nullable=True)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="tax_configs")
