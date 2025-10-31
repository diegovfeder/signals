"""
Database utilities shared across Prefect tasks.
"""

import os
from urllib.parse import urlparse

import psycopg
from dotenv import load_dotenv

load_dotenv()

# Parse and log database connection info on module import (without credentials)
_db_url = os.getenv("DATABASE_URL", "postgresql://quantmaster:buysthedip@localhost:5432/signals")
_parsed = urlparse(_db_url)
_db_host = _parsed.hostname or "unknown"
_db_port = _parsed.port or "unknown"
_db_name = _parsed.path.lstrip('/') if _parsed.path else "unknown"
print(f"[DB] Database connection: {_db_host}:{_db_port}/{_db_name}")


def get_db_conn():
    """Return a psycopg connection using DATABASE_URL (accepts SQLAlchemy-style URLs)."""
    db_url = os.getenv("DATABASE_URL", "postgresql://quantmaster:buysthedip@localhost:5432/signals")
    if "+psycopg" in db_url:
        scheme, remainder = db_url.split("://", 1)
        scheme = scheme.split("+", 1)[0]
        db_url = f"{scheme}://{remainder}"
    return psycopg.connect(db_url)
