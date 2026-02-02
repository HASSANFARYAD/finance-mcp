from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate

def create_expense(db: Session, expense_data: ExpenseCreate, owner_id: int):
    expense = Expense(**expense_data.dict(), owner_id=owner_id)
    if expense_data.date is None:
        expense.date = func.now()
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense

def get_expenses(db: Session, owner_id: int):
    return db.query(Expense).filter(Expense.owner_id == owner_id).all()

def get_expense(db: Session, expense_id: int, owner_id: int):
    return db.query(Expense).filter(Expense.id == expense_id, Expense.owner_id == owner_id).first()

def update_expense(db: Session, expense_id: int, update_data: dict, owner_id: int):
    expense = get_expense(db, expense_id, owner_id)
    if expense:
        for key, value in update_data.items():
            if value is not None:
                setattr(expense, key, value)
        db.commit()
        db.refresh(expense)
    return expense
