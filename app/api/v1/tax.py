from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user
from app.schemas.tax_config import TaxConfigCreate, TaxConfigOut
from app.crud.tax_config import create_tax_config, list_tax_configs
from app.models.user import User

router = APIRouter()


@router.post("/configs", response_model=TaxConfigOut, summary="Create a tax configuration")
def create_tax(data: TaxConfigCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_tax_config(db, current_user.id, data)


@router.get("/configs", response_model=list[TaxConfigOut], summary="List tax configurations")
def list_tax(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return list_tax_configs(db, current_user.id)
