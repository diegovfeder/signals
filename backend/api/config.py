"""
Configuration Management

Load environment variables and application settings.
"""

from pydantic_settings import BaseSettings
from typing import List
from pydantic import field_validator


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

    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """
        Parse CORS_ORIGINS from environment variable.
        
        Supports:
        - JSON array: '["http://localhost:3000", "https://example.com"]'
        - Comma-separated: 'http://localhost:3000,https://example.com'
        - Single value: 'http://localhost:3000'
        """
        if isinstance(v, str):
            # Try to parse as JSON first
            import json
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                pass
            
            # Parse as comma-separated values
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
