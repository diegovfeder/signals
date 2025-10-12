"""
Configuration Management

Load environment variables and application settings.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Database
    DATABASE_URL: str

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Email Service
    RESEND_API_KEY: str = ""

    # Environment
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
