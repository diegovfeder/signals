"""
Configuration Management

Load environment variables and application settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Database
    DATABASE_URL: str

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True

    # CORS (expects JSON array format in .env: ["http://localhost:3000"])
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Email Service
    RESEND_API_KEY: str = ""

    # Environment
    ENVIRONMENT: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


# Global settings instance (loads from .env automatically via BaseSettings)
settings = Settings()  # type: ignore[call-arg]
