from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./data.db"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200
    RATE_LIMIT_PER_MINUTE: int = 120  # simple in-memory limiter
    REDIS_URL: str | None = None      # if set, rate limiting uses Redis
    REQUIRE_HTTPS: bool = True        # enforce HTTPS by default
    MCP_HOST: str = "0.0.0.0"
    MCP_PORT: int = 9000
    MCP_AUTH_REQUIRED: bool = True
    MCP_DEFAULT_OWNER_ID: int | None = None

    model_config = {"env_file": ".env"}

settings = Settings()
