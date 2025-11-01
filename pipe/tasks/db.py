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
    return psycopg.connect(database_url)
