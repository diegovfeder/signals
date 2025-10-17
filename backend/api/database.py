"""
Database Connection and Session Management

SQLAlchemy setup for PostgreSQL.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from .config import settings

# Create database engine with appropriate pooling strategy
# For serverless environments (Vercel), use NullPool to avoid connection exhaustion
# For traditional deployments, use small pool to prevent database connection limit issues
if settings.ENVIRONMENT == "production" or settings.ENVIRONMENT == "serverless":
    # NullPool: No connection pooling - creates new connection per request
    # Best for serverless where each function instance is isolated
    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=NullPool,
        pool_pre_ping=True,
        echo=False
    )
else:
    # Development: Small connection pool
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=5,  # Reduced from 10
        max_overflow=5,  # Reduced from 20
        pool_recycle=3600,  # Recycle connections after 1 hour
        echo=False
    )

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
    
    Note: Session is automatically closed even if an exception occurs during request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
