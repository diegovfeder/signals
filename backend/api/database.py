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

# Configure engine based on environment
if settings.ENVIRONMENT == "production":
    # Serverless environment (Vercel) - use NullPool to prevent connection exhaustion
    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=NullPool,  # No connection pooling in serverless
        pool_pre_ping=True,
    )
    logger.info("Database engine configured for serverless (NullPool)")
else:
    # Development environment - use connection pooling
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )
    logger.info("Database engine configured for development (connection pooling)")

# Log database connection info (without credentials)
parsed_url = urlparse(settings.DATABASE_URL)
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
