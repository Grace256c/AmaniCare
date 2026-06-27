"""Application configuration loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for MamaCare AI backend."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "MamaCare AI"
    app_version: str = "1.0.0"
    debug: bool = False

    database_url: str = Field(
        default="sqlite+aiosqlite:///./mamacare.db",
        description="SQLAlchemy database URL. PostgreSQL recommended for production.",
    )

    google_api_key: str = Field(default="", description="Google Gemini API key")
    gemini_model: str = Field(
        default="gemini-2.0-flash",
        description="Gemini model identifier",
    )

    africas_talking_username: str = Field(default="")
    africas_talking_api_key: str = Field(default="")

    secret_key: str = Field(default="change-me-in-production")

    cors_origins: list[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins for the Next.js frontend",
    )

    log_level: Literal["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"] = "INFO"


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
