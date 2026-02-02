from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.invoice import Invoice
from app.models.expense import Expense
from app.models.user import User

router = APIRouter()


@router.get("/reports/summary", summary="Totals for invoices and expenses")
def summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    inv_sum = (
        db.query(
            func.coalesce(func.sum(Invoice.total), 0).label("total"),
            func.count(Invoice.id).label("count"),
        )
        .filter(Invoice.owner_id == current_user.id)
        .first()
    )
    exp_sum = (
        db.query(
            func.coalesce(func.sum(Expense.amount), 0).label("total"),
            func.count(Expense.id).label("count"),
        )
        .filter(Expense.owner_id == current_user.id)
        .first()
    )
    return {
        "invoices": {"count": int(inv_sum.count), "total": str(inv_sum.total)},
        "expenses": {"count": int(exp_sum.count), "total": str(exp_sum.total)},
    }


@router.get("/reports/monthly", summary="Monthly totals for invoices and expenses")
def monthly(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    invoices = (
        db.query(
            func.strftime("%Y-%m", Invoice.created_at).label("month"),
            func.coalesce(func.sum(Invoice.total), 0).label("total"),
        )
        .filter(Invoice.owner_id == current_user.id)
        .group_by("month")
        .all()
    )
    expenses = (
        db.query(
            func.strftime("%Y-%m", Expense.created_at).label("month"),
            func.coalesce(func.sum(Expense.amount), 0).label("total"),
        )
        .filter(Expense.owner_id == current_user.id)
        .group_by("month")
        .all()
    )
    return {
        "invoices": [{"month": m.month, "total": str(m.total)} for m in invoices],
        "expenses": [{"month": m.month, "total": str(m.total)} for m in expenses],
    }
