import secrets
import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.api_key import ApiKey


def _hash_key(plain_key: str) -> str:
    return hashlib.sha256(plain_key.encode("utf-8")).hexdigest()


def generate_api_key(owner_id: int, name: str | None = None) -> tuple[str, str, str]:
    random_part = secrets.token_urlsafe(32)
    plain_key = f"mcp_u{owner_id}_{random_part}"
    prefix = plain_key[:12]  # first 12 chars for index
    hashed = _hash_key(plain_key)
    return plain_key, hashed, prefix


def create_api_key(db: Session, owner_id: int, name: str | None = None, ttl_days: int | None = None) -> tuple[ApiKey, str]:
    plain, hashed, prefix = generate_api_key(owner_id, name)
    expires_at = None
    if ttl_days:
        expires_at = datetime.now(timezone.utc) + timedelta(days=ttl_days)
    api_key = ApiKey(name=name, key_hash=hashed, key_prefix=prefix, owner_id=owner_id, expires_at=expires_at)
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    return api_key, plain


def verify_api_key_plain(plain_key: str, key_obj: ApiKey) -> bool:
    if key_obj.expires_at and datetime.now(timezone.utc) > key_obj.expires_at:
        return False
    ok = hmac.compare_digest(_hash_key(plain_key), key_obj.key_hash)
    if ok:
        key_obj.last_used_at = datetime.now(timezone.utc)
    return ok


def get_user_api_keys(db: Session, owner_id: int):
    return db.query(ApiKey).filter(ApiKey.owner_id == owner_id).all()


def list_api_keys(db: Session, owner_id: int):
    """Alias for clarity in routers."""
    return get_user_api_keys(db, owner_id)


def delete_api_key(db: Session, key_id: int, owner_id: int):
    key = db.query(ApiKey).filter(ApiKey.id == key_id, ApiKey.owner_id == owner_id).first()
    if key:
        db.delete(key)
        db.commit()
        return True
    return False
