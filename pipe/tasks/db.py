"""
Database utilities shared across Prefect tasks.
"""

import os

import psycopg
from dotenv import load_dotenv

load_dotenv()


def get_db_conn():
    """Return a psycopg connection using DATABASE_URL (accepts SQLAlchemy-style URLs)."""
    db_url = os.getenv("DATABASE_URL", "postgresql://quantmaster:buysthedip@localhost:5432/signals")
    if "+psycopg" in db_url:
        scheme, remainder = db_url.split("://", 1)
        scheme = scheme.split("+", 1)[0]
        db_url = f"{scheme}://{remainder}"
    return psycopg.connect(db_url)
