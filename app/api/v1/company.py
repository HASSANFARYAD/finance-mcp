from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import os
from app.db.session import get_db
from app.core.security import get_current_user
from app.schemas.company_profile import CompanyProfileOut, CompanyProfileUpdate
from app.crud.company_profile import get_or_create_profile, update_profile
from app.models.user import User

router = APIRouter()


@router.get("/company/profile", response_model=CompanyProfileOut)
def fetch_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    profile = get_or_create_profile(db, current_user.id)
    return profile


@router.patch("/company/profile", response_model=CompanyProfileOut)
def edit_profile(data: CompanyProfileUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return update_profile(db, current_user.id, data)


@router.post("/company/logo", response_model=CompanyProfileOut)
def upload_logo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "Only image uploads allowed")
    os.makedirs("logos", exist_ok=True)
    filename = f"logos/{current_user.id}_{file.filename}"
    with open(filename, "wb") as f:
        f.write(file.file.read())
    profile = get_or_create_profile(db, current_user.id)
    profile.logo_path = filename
    db.commit()
    db.refresh(profile)
    return profile
