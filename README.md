# Modular Financial Protocols (MCP)

Minimal FastAPI service for invoices, expenses, auth (JWT + API keys). Runs on SQLite by default (no external DB). Switch to Postgres by setting `DATABASE_URL`.

## Quick start (no database provisioning)
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
# API at http://127.0.0.1:8000
# Docs at http://127.0.0.1:8000/docs
```

## MCP SSE server (for Syntellio)
This repo now exposes an MCP-compatible SSE server so Syntellio can call finance tools.

```bash
pip install -r requirements.txt
python -m app.mcp_server
# MCP SSE at http://127.0.0.1:8080/sse
```

Auth:
- Send `Authorization: Bearer <jwt>` or `x-api-key: <key>` headers with tool calls.
- To disable auth for local testing, set `MCP_AUTH_REQUIRED=false` and set `MCP_DEFAULT_OWNER_ID` to a valid user id.

Syntellio config:
- Set `MCP_SERVER_URL` to `http://<host>:8080/sse`.
- Ensure the MCP client sends the same auth headers if enabled.

## Tool catalog (discovery)
`GET /api/v1/tools` returns a machine-readable list of available modules/endpoints with their input/output fields.

## Security notes
- API keys are only shown on creation; you can revoke via `DELETE /api/v1/auth/api-keys/{id}`.
- In-memory rate limiting: default 120 requests/min per API key or IP (config `RATE_LIMIT_PER_MINUTE`).
- For production: enforce HTTPS at the proxy/load balancer, rotate keys periodically, and use an external rate limiter (Redis) instead of the built-in memory limiter.

## Deploy to Render (one-click)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/your/repo)

Manual steps if you prefer:
1) Push this repo to GitHub.
2) Render: New Web Service → Runtime: Python 3 → Build `pip install -r requirements.txt` → Start `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
3) Env: set `SECRET_KEY` (strong random). Leave `DATABASE_URL` empty to use SQLite, or set a Postgres URL.

## ENV
- `DATABASE_URL` (default `sqlite:///./data.db`)
- `SECRET_KEY` (required in production)
- `ALGORITHM` (default HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` (default 43200)
- `RATE_LIMIT_PER_MINUTE` (default 120)
- `REDIS_URL` (optional; enables Redis-backed rate limiting for multi-instance)
- `REQUIRE_HTTPS` (default true; set false for local/dev)

## Tests
```bash
pytest -q
```

## Seed demo data
```bash
python seed.py
```

## Switch to Postgres
Set `DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/db` and run `alembic upgrade head` once.
