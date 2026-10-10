"""
Application configuration.

Loads settings from .env file using pydantic-settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ─── App ───
    APP_NAME: str = "Autonomous AI Agent Platform"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-in-production"

    # ─── Database ───
    # SQLite for now - easy to switch to PostgreSQL later
    DATABASE_URL: str = "sqlite:///./aiagent.db"

    # ─── Redis (optional for now) ───
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # ─── LLM ───
    LLM_PROVIDER: str = "openai"
    OPENAI_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_MAX_TOKENS: int = 2000
    LLM_TEMPERATURE: float = 0.2

    # ─── JWT ───
    JWT_SECRET: str = "change-me-too"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    # ─── Pydantic Config ───
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# Single instance to import everywhere
settings = Settings()
