from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.crud.user import create_user, get_user_by_email
from app.schemas.user import UserCreate, Token
from app.core.security import create_access_token, get_current_user
from app.models.user import User
from app.schemas.api_key import ApiKeyCreate, ApiKeyOut, ApiKeyFullOut
from app.schemas.api_key_rotate import ApiKeyRotate
from app.crud.api_key import create_api_key, list_api_keys, delete_api_key
from app.crud.api_key import delete_api_key, create_api_key

router = APIRouter()

@router.post("/register", response_model=Token)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing = get_user_by_email(db, user_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = create_user(db, user_data.email, user_data.password)
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_email(db, form_data.username)
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/api-keys", response_model=ApiKeyFullOut)
def generate_api_key(
    data: ApiKeyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    api_key_obj, plain_key = create_api_key(db, current_user.id, data.name, ttl_days=data.ttl_days)
    return {**ApiKeyOut.from_orm(api_key_obj).dict(), "plain_key": plain_key}

@router.get("/api-keys", response_model=list[ApiKeyOut])
def list_my_api_keys(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return list_api_keys(db, current_user.id)

@router.delete("/api-keys/{key_id}")
def revoke_api_key(key_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if delete_api_key(db, key_id, current_user.id):
        return {"status": "revoked"}
    raise HTTPException(404, "API key not found")


@router.post("/api-keys/{key_id}/rotate", response_model=ApiKeyFullOut)
def rotate_api_key(
    key_id: int,
    data: ApiKeyRotate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # delete old key, create new with same/updated name and ttl
    if not delete_api_key(db, key_id, current_user.id):
        raise HTTPException(404, "API key not found")
    api_key_obj, plain_key = create_api_key(
        db,
        current_user.id,
        data.name,
        ttl_days=data.ttl_days,
    )
    return {**ApiKeyOut.from_orm(api_key_obj).dict(), "plain_key": plain_key}
