from fastapi import APIRouter
from .auth import router as auth_router
from .invoicing import router as invoicing_router
from .expenses import router as expenses_router
from .tools import router as tools_router
from .reporting import router as reporting_router
from .tax import router as tax_router
from .company import router as company_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(invoicing_router, prefix="/invoices", tags=["invoices"])
router.include_router(expenses_router, prefix="/expenses", tags=["expenses"])
router.include_router(tools_router, tags=["tools"])
router.include_router(reporting_router, tags=["reports"])
router.include_router(tax_router, prefix="/tax", tags=["tax"])
router.include_router(company_router, tags=["company"])
