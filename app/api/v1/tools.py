from fastapi import APIRouter

router = APIRouter()


@router.get("/tools", summary="List available MCP modules and their I/O schemas")
@router.get("/tools/", include_in_schema=False)
def list_tools():
    """
    Returns a static catalog of available modules/endpoints with expected inputs/outputs.
    This helps integrators discover capabilities without reading code.
    """
    tools = [
        {
            "name": "auth.register",
            "method": "POST",
            "path": "/api/v1/auth/register",
            "input": {"email": "string", "password": "string"},
            "output": {"access_token": "string", "token_type": "string"},
        },
        {
            "name": "auth.login",
            "method": "POST",
            "path": "/api/v1/auth/login",
            "input": {"username": "string (email)", "password": "string"},
            "output": {"access_token": "string", "token_type": "string"},
        },
        {
            "name": "auth.api-keys.create",
            "method": "POST",
            "path": "/api/v1/auth/api-keys",
            "input": {"name": "string|null", "ttl_days": "int|null"},
            "output": {"id": "int", "name": "string|null", "created_at": "datetime", "plain_key": "string"},
        },
        {
            "name": "auth.api-keys.list",
            "method": "GET",
            "path": "/api/v1/auth/api-keys",
            "input": {},
            "output": [{"id": "int", "name": "string|null", "created_at": "datetime"}],
        },
        {
            "name": "auth.api-keys.rotate",
            "method": "POST",
            "path": "/api/v1/auth/api-keys/{id}/rotate",
            "input": {"name": "string|null", "ttl_days": "int|null"},
            "output": {"id": "int", "name": "string|null", "created_at": "datetime", "plain_key": "string"},
        },
        {
            "name": "invoices.create",
            "method": "POST",
            "path": "/api/v1/invoices",
            "input": {
                "invoice_number": "string",
                "due_date": "datetime",
                "client_name": "string",
                "client_email": "string|null",
                "currency": "string",
                "tax_rate": "decimal|null",
                "tax_label": "string|null",
                "tax_note": "string|null",
                "items": [{"description": "string", "quantity": "decimal", "unit_price": "decimal"}],
            },
            "output": "InvoiceOut",
        },
        {
            "name": "invoices.list",
            "method": "GET",
            "path": "/api/v1/invoices",
            "input": {},
            "output": ["InvoiceOut"],
        },
        {
            "name": "invoices.pdf",
            "method": "GET",
            "path": "/api/v1/invoices/{id}/pdf",
            "input": {},
            "output": "application/pdf",
        },
        {
            "name": "invoices.qrcode",
            "method": "GET",
            "path": "/api/v1/invoices/{id}/qrcode",
            "input": {},
            "output": "image/png",
        },
        {
            "name": "invoices.email",
            "method": "POST",
            "path": "/api/v1/invoices/{id}/email",
            "input": {"to": "email"},
            "output": {"status": "queued", "note": "string"},
        },
        {
            "name": "expenses.create",
            "method": "POST",
            "path": "/api/v1/expenses",
            "input": {
                "date": "datetime|null",
                "amount": "decimal",
                "currency": "string",
                "category": "string",
                "description": "string|null",
            },
            "output": "ExpenseOut",
        },
        {
            "name": "expenses.list",
            "method": "GET",
            "path": "/api/v1/expenses",
            "input": {},
            "output": ["ExpenseOut"],
        },
        {
            "name": "expenses.upload_receipt",
            "method": "POST",
            "path": "/api/v1/expenses/{id}/receipt",
            "input": {"file": "multipart image/pdf"},
            "output": "ExpenseOut",
        },
        {
            "name": "reports.summary",
            "method": "GET",
            "path": "/api/v1/reports/summary",
            "input": {},
            "output": {"invoices": {"count": "int", "total": "decimal"}, "expenses": {"count": "int", "total": "decimal"}},
        },
        {
            "name": "reports.monthly",
            "method": "GET",
            "path": "/api/v1/reports/monthly",
            "input": {},
            "output": {"invoices": [{"month": "YYYY-MM", "total": "decimal"}], "expenses": [{"month": "YYYY-MM", "total": "decimal"}]},
        },
        {
            "name": "tax.configs.create",
            "method": "POST",
            "path": "/api/v1/tax/configs",
            "input": {"name": "string", "country": "string|null", "rate": "decimal", "label": "string|null", "note": "string|null"},
            "output": "TaxConfigOut",
        },
        {
            "name": "tax.configs.list",
            "method": "GET",
            "path": "/api/v1/tax/configs",
            "input": {},
            "output": ["TaxConfigOut"],
        },
        {
            "name": "company.profile.get",
            "method": "GET",
            "path": "/api/v1/company/profile",
            "input": {},
            "output": "CompanyProfileOut",
        },
        {
            "name": "company.profile.update",
            "method": "PATCH",
            "path": "/api/v1/company/profile",
            "input": {"header_text": "string|null", "tax_label": "string|null", "tax_note": "string|null"},
            "output": "CompanyProfileOut",
        },
        {
            "name": "company.logo.upload",
            "method": "POST",
            "path": "/api/v1/company/logo",
            "input": {"file": "multipart image"},
            "output": "CompanyProfileOut",
        },
    ]
    return {"modules": tools}
