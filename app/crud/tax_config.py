from sqlalchemy.orm import Session
from app.models.tax_config import TaxConfig
from app.schemas.tax_config import TaxConfigCreate


def create_tax_config(db: Session, owner_id: int, data: TaxConfigCreate):
    cfg = TaxConfig(
        name=data.name,
        country=data.country,
        rate=data.rate,
        owner_id=owner_id,
    )
    db.add(cfg)
    db.commit()
    db.refresh(cfg)
    return cfg


def list_tax_configs(db: Session, owner_id: int):
    return db.query(TaxConfig).filter(TaxConfig.owner_id == owner_id).all()


def get_default_tax_rate(db: Session, owner_id: int) -> float | None:
    cfg = (
        db.query(TaxConfig)
        .filter(TaxConfig.owner_id == owner_id)
        .order_by(TaxConfig.id.asc())
        .first()
    )
    return float(cfg.rate) if cfg else None
