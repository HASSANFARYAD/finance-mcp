from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base


class CompanyProfile(Base):
    __tablename__ = "company_profiles"
    __table_args__ = (UniqueConstraint("owner_id", name="uq_company_profile_owner"),)

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    logo_path = Column(String, nullable=True)
    header_text = Column(String, nullable=True)
    tax_label = Column(String, nullable=True)
    tax_note = Column(String, nullable=True)

    owner = relationship("User", back_populates="company_profile")
