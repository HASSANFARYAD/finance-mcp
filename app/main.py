import os
from fastapi import FastAPI
from app.api.v1.router import router as v1_router
from app.models.base import Base
from app.db.session import engine
from app.core.config import settings
from app.core.ratelimit import build_limiter, SimpleRateLimiter

app = FastAPI(
    title="Modular Financial Protocols (MCP)",
    description="Open-source financial toolkit API",
    version="0.1.0"
)

app.include_router(v1_router, prefix="/api/v1")


@app.on_event("startup")
def create_sqlite_schema_if_needed():
    """
    Auto-create tables when using the default SQLite URL so users can run
    without provisioning an external database. For Postgres, use Alembic.
    """
    if settings.DATABASE_URL.startswith("sqlite"):
        Base.metadata.create_all(bind=engine)
    # initialize limiter instance on app state so tests can override/reset
    app.state.limiter = build_limiter(settings.REDIS_URL, settings.RATE_LIMIT_PER_MINUTE, 60)


@app.middleware("http")
async def rate_limit(request, call_next):
    limiter = getattr(app.state, "limiter", build_limiter(settings.REDIS_URL, settings.RATE_LIMIT_PER_MINUTE, 60))
    # key by api-key if present, else client host
    key = request.headers.get("x-api-key") or request.client.host
    limiter.check(key)
    # HTTPS enforcement (except localhost or disabled)
    if settings.REQUIRE_HTTPS:
        proto = request.headers.get("x-forwarded-proto") or request.url.scheme
        host = request.headers.get("host", "")
        if proto != "https" and not host.startswith("127.0.0.1") and not host.startswith("localhost"):
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="HTTPS required")

    response = await call_next(request)
    return response
