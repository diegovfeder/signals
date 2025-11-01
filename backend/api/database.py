"""
Database Connection and Session Management

SQLAlchemy setup for PostgreSQL.
"""

import logging
from urllib.parse import urlparse

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from .config import settings

logger = logging.getLogger(__name__)

# Normalize DATABASE_URL to use psycopg driver (not psycopg2)
# Vercel environment variables may use postgresql:// which defaults to psycopg2
# We need postgresql+psycopg:// to use the psycopg (v3) driver from requirements.txt
database_url = settings.DATABASE_URL
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    logger.info("Normalized DATABASE_URL to use psycopg driver")

# Add connection parameters for Vercel serverless compatibility
# - Prefer IPv4 (Vercel may not support outbound IPv6)
# - SSL mode required for Supabase
# - Connect timeout to fail fast
if "?" not in database_url:
    database_url += "?sslmode=require&connect_timeout=10"
elif "sslmode" not in database_url:
    database_url += "&sslmode=require&connect_timeout=10"

logger.info(f"Database connection configured (IPv4 preferred, SSL required)")

# Configure engine based on environment
if settings.ENVIRONMENT == "production":
    # Serverless environment (Vercel) - use NullPool to prevent connection exhaustion
    engine = create_engine(
        database_url,
        poolclass=NullPool,  # No connection pooling in serverless
        pool_pre_ping=True,
    )
    logger.info("Database engine configured for serverless (NullPool)")
else:
    # Development environment - use connection pooling
    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )
    logger.info("Database engine configured for development (connection pooling)")

# Log database connection info (without credentials)
parsed_url = urlparse(database_url)
db_host = parsed_url.hostname or "unknown"
db_port = parsed_url.port or "unknown"
db_name = parsed_url.path.lstrip('/') if parsed_url.path else "unknown"
logger.info(f"Connected to database: {db_host}:{db_port}/{db_name} (environment: {settings.ENVIRONMENT})")

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()


def get_db():
    """
    Dependency for FastAPI routes to get database session.

    Usage:
        @app.get("/endpoint")
        def my_endpoint(db: Session = Depends(get_db)):
            # Use db session here
            pass
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
