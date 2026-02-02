"""
Seed script to create demo data and a demo API key.
Usage:
    DATABASE_URL=postgresql+psycopg2://... SECRET_KEY=... python seed.py
Run inside container:
    docker-compose run --rm api python seed.py
"""
import os
from datetime import datetime
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.user import User
from app.models.invoice import Invoice, InvoiceItem, InvoiceStatus
from app.models.expense import Expense, ExpenseStatus
from app.crud.api_key import create_api_key
from app.core.config import settings

DATABASE_URL = os.getenv("DATABASE_URL", settings.DATABASE_URL)


def main():
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(engine)

    db = SessionLocal()
    try:
        # create demo user if not exists
        user = db.query(User).filter_by(email="demo@mcp.dev").first()
        if not user:
            user = User(email="demo@mcp.dev", hashed_password=User.get_password_hash("Passw0rd!"))
            db.add(user)
            db.commit()
            db.refresh(user)

        # invoices
        if not db.query(Invoice).filter_by(owner_id=user.id).first():
            inv1 = Invoice(
                invoice_number="INV-1001",
                client_name="Acme Corp",
                client_email="billing@acme.com",
                due_date=datetime.fromisoformat("2026-03-01"),
                currency="USD",
                subtotal=Decimal("1500.00"),
                tax_amount=Decimal("150.00"),
                total=Decimal("1650.00"),
                status=InvoiceStatus.sent,
                owner_id=user.id,
            )
            db.add(inv1)
            db.commit()
            db.refresh(inv1)
            db.add_all(
                [
                    InvoiceItem(
                        description="Consulting Hours",
                        quantity=Decimal("10"),
                        unit_price=Decimal("100.00"),
                        line_total=Decimal("1000.00"),
                        invoice_id=inv1.id,
                        owner_id=user.id,
                    ),
                    InvoiceItem(
                        description="Implementation",
                        quantity=Decimal("1"),
                        unit_price=Decimal("500.00"),
                        line_total=Decimal("500.00"),
                        invoice_id=inv1.id,
                        owner_id=user.id,
                    ),
                ]
            )

            inv2 = Invoice(
                invoice_number="INV-1002",
                client_name="Globex Ltd",
                client_email="ap@globex.com",
                due_date=datetime.fromisoformat("2026-03-15"),
                currency="EUR",
                subtotal=Decimal("800.00"),
                tax_amount=Decimal("0.00"),
                total=Decimal("800.00"),
                status=InvoiceStatus.draft,
                owner_id=user.id,
            )
            db.add(inv2)
            db.commit()
            db.refresh(inv2)
            db.add(
                InvoiceItem(
                    description="Subscription",
                    quantity=Decimal("12"),
                    unit_price=Decimal("66.67"),
                    line_total=Decimal("800.04"),
                    invoice_id=inv2.id,
                    owner_id=user.id,
                )
            )

        # expenses
        if not db.query(Expense).filter_by(owner_id=user.id).first():
            db.add_all(
                [
                    Expense(
                        amount=Decimal("120.50"),
                        currency="USD",
                        category="Travel",
                        description="Taxi to client",
                        status=ExpenseStatus.approved,
                        owner_id=user.id,
                    ),
                    Expense(
                        amount=Decimal("45.00"),
                        currency="USD",
                        category="Meals",
                        description="Team lunch",
                        status=ExpenseStatus.pending,
                        owner_id=user.id,
                    ),
                    Expense(
                        amount=Decimal("300.00"),
                        currency="EUR",
                        category="Software",
                        description="SaaS subscription",
                        status=ExpenseStatus.reimbursed,
                        owner_id=user.id,
                    ),
                ]
            )

        db.commit()

        # create an API key each run (idempotent-ish by naming)
        from app.models.api_key import ApiKey

        if not db.query(ApiKey).filter(ApiKey.owner_id == user.id, ApiKey.name == "demo-key").first():
            api_key_obj, plain = create_api_key(db, user.id, name="demo-key")
            print("Demo API key (store safely):", plain)
        else:
            print("Demo API key already exists. Create a new one via /api/v1/auth/api-keys if needed.")

        print("Seed complete. Demo user: demo@mcp.dev / Passw0rd!")
    finally:
        db.close()


if __name__ == "__main__":
    main()
