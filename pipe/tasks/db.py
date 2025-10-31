"""
Database utilities shared across Prefect tasks.
"""

from __future__ import annotations

import os
import socket
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import psycopg
from dotenv import load_dotenv

load_dotenv()


def _normalize_db_url(raw_url: str) -> str:
    """Normalize SQLAlchemy-style URLs and prefer IPv4 connections."""
    if "+psycopg" in raw_url:
        scheme, remainder = raw_url.split("://", 1)
        scheme = scheme.split("+", 1)[0]
        raw_url = f"{scheme}://{remainder}"

    parsed = urlparse(raw_url)
    host = parsed.hostname
    port = parsed.port or 5432
    if not host:
        return raw_url

    try:
        ipv4_candidates = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
    except socket.gaierror:
        ipv4_candidates = []

    if ipv4_candidates:
        ipv4 = ipv4_candidates[0][4][0]
        query = {key: value for key, value in parse_qsl(parsed.query, keep_blank_values=True)}
        if host not in {"localhost", "127.0.0.1"}:
            query.setdefault("sslmode", "require")
        query["hostaddr"] = str(ipv4)
        raw_url = urlunparse(parsed._replace(query=urlencode(query)))

    return raw_url


def _log_db_info(db_url: str) -> None:
    parsed = urlparse(db_url)
    host = parsed.hostname or "unknown"
    port = parsed.port or "unknown"
    name = parsed.path.lstrip("/") if parsed.path else "unknown"
    print(f"[DB] Database connection: {host}:{port}/{name}")


_CONFIGURED_DB_URL = os.getenv("DATABASE_URL", "postgresql://quantmaster:buysthedip@localhost:5432/signals")
_NORMALIZED_DB_URL = _normalize_db_url(_CONFIGURED_DB_URL)
_log_db_info(_NORMALIZED_DB_URL)


def get_db_conn():
    """Return a psycopg connection using DATABASE_URL (accepts SQLAlchemy-style URLs)."""
    return psycopg.connect(_NORMALIZED_DB_URL)
