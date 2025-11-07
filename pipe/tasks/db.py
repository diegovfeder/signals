"""
Database utilities shared across Prefect tasks.
"""

import os
import psycopg
from dotenv import load_dotenv

_ = load_dotenv()


def get_db_conn() -> psycopg.Connection:
    """Return a psycopg connection using DATABASE_URL."""
    database_url = os.getenv(
        "DATABASE_URL", "postgresql://quantmaster:buysthedip@localhost:5432/signals"
    )
    # Strip SQLAlchemy driver suffix if present (e.g., postgresql+psycopg://)
    # This allows the same .env to work for both backend (SQLAlchemy) and pipeline (psycopg3)
    database_url = database_url.replace("postgresql+psycopg://", "postgresql://")
    return psycopg.connect(database_url)
