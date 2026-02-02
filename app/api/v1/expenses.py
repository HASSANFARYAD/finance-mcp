from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.expense import ExpenseCreate, ExpenseOut, ExpenseUpdate
from app.crud.expense import create_expense, get_expenses, get_expense, update_expense
from app.core.security import get_current_user
from app.models.user import User
import os

router = APIRouter()

@router.post("/", response_model=ExpenseOut)
def create_new_expense(expense_data: ExpenseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_expense(db, expense_data, current_user.id)

@router.get("/", response_model=list[ExpenseOut])
def list_expenses(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_expenses(db, current_user.id)

@router.get("/{expense_id}", response_model=ExpenseOut)
def retrieve_expense(expense_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    expense = get_expense(db, expense_id, current_user.id)
    if not expense:
        raise HTTPException(404)
    return expense

@router.patch("/{expense_id}", response_model=ExpenseOut)
def update_existing_expense(expense_id: int, update: ExpenseUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    data = update.dict(exclude_unset=True)
    expense = update_expense(db, expense_id, data, current_user.id)
    if not expense:
        raise HTTPException(404)
    return expense


@router.post("/{expense_id}/receipt", response_model=ExpenseOut)
def upload_receipt(
    expense_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = get_expense(db, expense_id, current_user.id)
    if not expense:
        raise HTTPException(404, "Expense not found")

    os.makedirs("receipts", exist_ok=True)
    filename = f"receipts/{current_user.id}_{expense_id}_{file.filename}"
    with open(filename, "wb") as f:
        f.write(file.file.read())

    expense.receipt_url = filename
    db.commit()
    db.refresh(expense)
    return expense
