from __future__ import annotations

from contextlib import contextmanager

from jose import JWTError, jwt
from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud.api_key import get_user_api_keys, verify_api_key_plain
from app.crud.company_profile import get_or_create_profile, update_profile
from app.crud.expense import create_expense, get_expense, get_expenses, update_expense
from app.crud.invoice import create_invoice, get_invoice, get_invoices, update_invoice_status
from app.crud.tax_config import create_tax_config, list_tax_configs
from app.crud.user import get_user_by_email, get_user_by_id
from app.db.session import SessionLocal, engine
from app.models.base import Base
from app.models.expense import Expense
from app.models.invoice import Invoice
from app.schemas.company_profile import CompanyProfileOut, CompanyProfileUpdate
from app.schemas.expense import ExpenseCreate, ExpenseOut, ExpenseUpdate
from app.schemas.invoice import InvoiceCreate, InvoiceOut
from app.schemas.tax_config import TaxConfigCreate, TaxConfigOut


class AuthError(ValueError):
    pass


class ReportTotals(BaseModel):
    count: int
    total: str


class SummaryReport(BaseModel):
    invoices: ReportTotals
    expenses: ReportTotals


class MonthlyItem(BaseModel):
    month: str
    total: str


class MonthlyReport(BaseModel):
    invoices: list[MonthlyItem]
    expenses: list[MonthlyItem]


@contextmanager
def db_session() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _get_headers(ctx: Context):
    request_context = getattr(ctx, "request_context", None)
    request = getattr(request_context, "request", None)
    if request is None or not hasattr(request, "headers"):
        raise AuthError("Request context is unavailable for authentication.")
    return request.headers


def _require_user(db: Session, ctx: Context):
    if not settings.MCP_AUTH_REQUIRED:
        if settings.MCP_DEFAULT_OWNER_ID is None:
            raise AuthError("MCP_AUTH_REQUIRED is false but MCP_DEFAULT_OWNER_ID is not set.")
        user = get_user_by_id(db, settings.MCP_DEFAULT_OWNER_ID)
        if not user:
            raise AuthError("Default owner user not found.")
        return user

    headers = _get_headers(ctx)
    authorization = headers.get("authorization")
    if authorization and authorization.startswith("Bearer "):
        token = authorization[len("Bearer ") :]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except JWTError as exc:
            raise AuthError("Invalid token.") from exc
        email = payload.get("sub")
        if not email:
            raise AuthError("Invalid token.")
        user = get_user_by_email(db, email)
        if not user:
            raise AuthError("User not found.")
        return user

    x_api_key = headers.get("x-api-key")
    if x_api_key:
        if not x_api_key.startswith("mcp_u"):
            raise AuthError("Invalid API key format.")
        parts = x_api_key.split("_", 2)
        if len(parts) != 3 or not parts[1].startswith("u"):
            raise AuthError("Invalid API key format.")
        try:
            user_id = int(parts[1][1:])
        except ValueError as exc:
            raise AuthError("Invalid API key format.") from exc

        user = get_user_by_id(db, user_id)
        if not user:
            raise AuthError("Invalid API key.")

        user_keys = get_user_api_keys(db, user_id)
        for key_obj in user_keys:
            if verify_api_key_plain(x_api_key, key_obj):
                db.commit()
                return user
        raise AuthError("Invalid API key.")

    raise AuthError("Missing credentials.")


mcp = FastMCP(
    name="Finance MCP",
    instructions=(
        "Finance tools for invoices, expenses, tax configs, company profile, and reporting."
    ),
    host=settings.MCP_HOST,
    port=settings.MCP_PORT,
)


@mcp.tool(name="invoices.create", description="Create a new invoice.")
def invoices_create(data: InvoiceCreate, ctx: Context) -> InvoiceOut:
    with db_session() as db:
        user = _require_user(db, ctx)
        invoice = create_invoice(db, data, user.id)
        return InvoiceOut.model_validate(invoice)


@mcp.tool(name="invoices.list", description="List invoices for the authenticated user.")
def invoices_list(ctx: Context, skip: int = 0, limit: int = 100) -> list[InvoiceOut]:
    with db_session() as db:
        user = _require_user(db, ctx)
        invoices = get_invoices(db, user.id, skip=skip, limit=limit)
        return [InvoiceOut.model_validate(inv) for inv in invoices]


@mcp.tool(name="invoices.get", description="Fetch a single invoice by ID.")
def invoices_get(invoice_id: int, ctx: Context) -> InvoiceOut:
    with db_session() as db:
        user = _require_user(db, ctx)
        invoice = get_invoice(db, invoice_id, user.id)
        if not invoice:
            raise ValueError("Invoice not found.")
        return InvoiceOut.model_validate(invoice)


@mcp.tool(name="invoices.update_status", description="Update an invoice status.")
def invoices_update_status(invoice_id: int, status: str, ctx: Context) -> InvoiceOut:
    with db_session() as db:
        user = _require_user(db, ctx)
        invoice = update_invoice_status(db, invoice_id, status, user.id)
        if not invoice:
            raise ValueError("Invoice not found.")
        return InvoiceOut.model_validate(invoice)


@mcp.tool(name="expenses.create", description="Create a new expense.")
def expenses_create(data: ExpenseCreate, ctx: Context) -> ExpenseOut:
    with db_session() as db:
        user = _require_user(db, ctx)
        expense = create_expense(db, data, user.id)
        return ExpenseOut.model_validate(expense)


@mcp.tool(name="expenses.list", description="List expenses for the authenticated user.")
def expenses_list(ctx: Context) -> list[ExpenseOut]:
    with db_session() as db:
        user = _require_user(db, ctx)
        expenses = get_expenses(db, user.id)
        return [ExpenseOut.model_validate(exp) for exp in expenses]


@mcp.tool(name="expenses.get", description="Fetch a single expense by ID.")
def expenses_get(expense_id: int, ctx: Context) -> ExpenseOut:
    with db_session() as db:
        user = _require_user(db, ctx)
        expense = get_expense(db, expense_id, user.id)
        if not expense:
            raise ValueError("Expense not found.")
        return ExpenseOut.model_validate(expense)


@mcp.tool(name="expenses.update", description="Update an expense.")
def expenses_update(expense_id: int, update: ExpenseUpdate, ctx: Context) -> ExpenseOut:
    with db_session() as db:
        user = _require_user(db, ctx)
        update_data = update.model_dump(exclude_unset=True)
        expense = update_expense(db, expense_id, update_data, user.id)
        if not expense:
            raise ValueError("Expense not found.")
        return ExpenseOut.model_validate(expense)


@mcp.tool(name="tax.configs.create", description="Create a tax configuration.")
def tax_configs_create(data: TaxConfigCreate, ctx: Context) -> TaxConfigOut:
    with db_session() as db:
        user = _require_user(db, ctx)
        cfg = create_tax_config(db, user.id, data)
        return TaxConfigOut.model_validate(cfg)


@mcp.tool(name="tax.configs.list", description="List tax configurations.")
def tax_configs_list(ctx: Context) -> list[TaxConfigOut]:
    with db_session() as db:
        user = _require_user(db, ctx)
        cfgs = list_tax_configs(db, user.id)
        return [TaxConfigOut.model_validate(cfg) for cfg in cfgs]


@mcp.tool(name="company.profile.get", description="Get the company profile.")
def company_profile_get(ctx: Context) -> CompanyProfileOut:
    with db_session() as db:
        user = _require_user(db, ctx)
        profile = get_or_create_profile(db, user.id)
        return CompanyProfileOut.model_validate(profile)


@mcp.tool(name="company.profile.update", description="Update the company profile.")
def company_profile_update(data: CompanyProfileUpdate, ctx: Context) -> CompanyProfileOut:
    with db_session() as db:
        user = _require_user(db, ctx)
        profile = update_profile(db, user.id, data)
        return CompanyProfileOut.model_validate(profile)


@mcp.tool(name="reports.summary", description="Totals for invoices and expenses.")
def reports_summary(ctx: Context) -> SummaryReport:
    with db_session() as db:
        user = _require_user(db, ctx)
        inv_sum = (
            db.query(
                func.coalesce(func.sum(Invoice.total), 0).label("total"),
                func.count(Invoice.id).label("count"),
            )
            .filter(Invoice.owner_id == user.id)
            .first()
        )
        exp_sum = (
            db.query(
                func.coalesce(func.sum(Expense.amount), 0).label("total"),
                func.count(Expense.id).label("count"),
            )
            .filter(Expense.owner_id == user.id)
            .first()
        )
        return SummaryReport(
            invoices=ReportTotals(count=int(inv_sum.count), total=str(inv_sum.total)),
            expenses=ReportTotals(count=int(exp_sum.count), total=str(exp_sum.total)),
        )


@mcp.tool(name="reports.monthly", description="Monthly totals for invoices and expenses.")
def reports_monthly(ctx: Context) -> MonthlyReport:
    with db_session() as db:
        user = _require_user(db, ctx)
        invoices = (
            db.query(
                func.strftime("%Y-%m", Invoice.created_at).label("month"),
                func.coalesce(func.sum(Invoice.total), 0).label("total"),
            )
            .filter(Invoice.owner_id == user.id)
            .group_by("month")
            .all()
        )
        expenses = (
            db.query(
                func.strftime("%Y-%m", Expense.created_at).label("month"),
                func.coalesce(func.sum(Expense.amount), 0).label("total"),
            )
            .filter(Expense.owner_id == user.id)
            .group_by("month")
            .all()
        )
        return MonthlyReport(
            invoices=[MonthlyItem(month=row.month, total=str(row.total)) for row in invoices],
            expenses=[MonthlyItem(month=row.month, total=str(row.total)) for row in expenses],
        )


def _ensure_sqlite_schema() -> None:
    if settings.DATABASE_URL.startswith("sqlite"):
        Base.metadata.create_all(bind=engine)


def main() -> None:
    _ensure_sqlite_schema()
    mcp.run(transport="sse")


if __name__ == "__main__":
    main()
