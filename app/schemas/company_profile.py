from pydantic import BaseModel


class CompanyProfileUpdate(BaseModel):
    header_text: str | None = None
    tax_label: str | None = None
    tax_note: str | None = None


class CompanyProfileOut(BaseModel):
    id: int
    logo_path: str | None
    header_text: str | None
    tax_label: str | None
    tax_note: str | None

    class Config:
        from_attributes = True
