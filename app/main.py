import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
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


@app.get("/health", include_in_schema=False)
def health():
    return {"status": "ok"}


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
    try:
        limiter.check(key)
        # HTTPS enforcement (except localhost or disabled)
        if settings.REQUIRE_HTTPS:
            # Only enforce when behind a proxy that sets X-Forwarded-Proto.
            # Direct Uvicorn connections are plain HTTP (TLS terminates at the proxy).
            forwarded_proto = request.headers.get("x-forwarded-proto")
            proto = forwarded_proto or request.url.scheme
            host = (request.headers.get("host", "") or "").split(":", 1)[0]
            insecure_ok_hosts = {"127.0.0.1", "localhost", "testserver"}
            if forwarded_proto and proto != "https" and host not in insecure_ok_hosts:
                raise HTTPException(status_code=400, detail="HTTPS required")
    except HTTPException as exc:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    response = await call_next(request)
    return response
