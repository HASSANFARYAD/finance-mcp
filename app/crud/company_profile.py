from sqlalchemy.orm import Session
from app.models.company_profile import CompanyProfile
from app.schemas.company_profile import CompanyProfileUpdate


def get_or_create_profile(db: Session, owner_id: int) -> CompanyProfile:
    profile = db.query(CompanyProfile).filter(CompanyProfile.owner_id == owner_id).first()
    if not profile:
        profile = CompanyProfile(owner_id=owner_id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def update_profile(db: Session, owner_id: int, data: CompanyProfileUpdate) -> CompanyProfile:
    profile = get_or_create_profile(db, owner_id)
    for k, v in data.dict(exclude_unset=True).items():
        setattr(profile, k, v)
    db.commit()
    db.refresh(profile)
    return profile
