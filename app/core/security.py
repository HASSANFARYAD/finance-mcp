from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from fastapi import Header, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from app.crud.user import get_user_by_email, get_user_by_id  # Ensure get_user_by_id exists
from app.crud.api_key import verify_api_key_plain, get_user_api_keys
from app.models.user import User

security = HTTPBearer()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

async def get_current_user(
    authorization: str | None = Header(None, alias="Authorization"),
    x_api_key: str | None = Header(None),
    db: Session = Depends(get_db)
):
    if authorization and authorization.startswith("Bearer "):
        # JWT logic (unchanged)
        token = authorization[len("Bearer "):]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email: str = payload.get("sub")
            if not email:
                raise HTTPException(status_code=401, detail="Invalid token")
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = get_user_by_email(db, email)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user

    elif x_api_key:
        if not x_api_key.startswith("mcp_u"):
            raise HTTPException(status_code=401, detail="Invalid API key format")
        
        try:
            parts = x_api_key.split("_", 2)
            if len(parts) != 3 or not parts[1].startswith("u"):
                raise ValueError
            user_id = int(parts[1][1:])
        except ValueError:
            raise HTTPException(status_code=401, detail="Invalid API key format")
        
        user = get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid API key")

        user_keys = get_user_api_keys(db, user_id)
        for key_obj in user_keys:
            if verify_api_key_plain(x_api_key, key_obj):
                db.commit()  # persist last_used_at
                return user

        raise HTTPException(status_code=401, detail="Invalid API key")

    raise HTTPException(status_code=401, detail="Missing credentials")

