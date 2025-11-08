"""
Configuration Management

Load environment variables and application settings.
"""

from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Database
    DATABASE_URL: str

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True

    # CORS - Allow localhost (dev) and all Vercel deployments (prod + previews)
    # Can override via env var with JSON array: ["https://example.com"]
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "https://signals-dvf.vercel.app",
        "https://*.vercel.app",  # All Vercel preview and production deployments
    ]

    # Email Service
    RESEND_API_KEY: str = ""

    # Environment
    ENVIRONMENT: str = "development"

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="ignore"
    )


def load_settings() -> "Settings":
    """Factory to keep static type checkers happy while loading from env."""

    return Settings()  # pyright: ignore[reportCallIssue]


# Global settings instance (loads from .env automatically via BaseSettings)
settings = load_settings()
