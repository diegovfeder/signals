"""
Database utilities shared across Prefect tasks.
"""

from __future__ import annotations

import os
import socket
from typing import Dict

import psycopg
from psycopg.conninfo import conninfo_to_dict
from dotenv import load_dotenv

load_dotenv()


def _prefer_ipv4(params: Dict[str, str]) -> Dict[str, str]:
    """Force connections over IPv4 when the host resolves to both families."""
    host = params.get("host")
    if not host or host in {"localhost", "127.0.0.1"}:
        return params

    port = int(params.get("port") or 5432)
    try:
        ipv4_candidates = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
    except socket.gaierror:
        return params
    if not ipv4_candidates:
        return params

    ipv4 = ipv4_candidates[0][4][0]
    params["hostaddr"] = ipv4
    params.setdefault("sslmode", "require")
    return params


def _log_db_info(params: Dict[str, str]) -> None:
    host = params.get("host", "unknown")
    hostaddr = params.get("hostaddr")
    port = params.get("port", "unknown")
    name = params.get("dbname", "unknown")
    if hostaddr and hostaddr != host:
        print(f"[DB] Database connection: {host} ({hostaddr}):{port}/{name}")
    else:
        print(f"[DB] Database connection: {host}:{port}/{name}")


def _load_connection_params() -> Dict[str, str]:
    raw_url = os.getenv("DATABASE_URL", "postgresql://quantmaster:buysthedip@localhost:5432/signals")
    if "+psycopg" in raw_url:
        scheme, remainder = raw_url.split("://", 1)
        scheme = scheme.split("+", 1)[0]
        raw_url = f"{scheme}://{remainder}"
    params = conninfo_to_dict(raw_url)
    params = _prefer_ipv4(params)
    params.setdefault("prepare_threshold", 0)
    return params


_CONN_PARAMS = _load_connection_params()
_log_db_info(_CONN_PARAMS)


def get_db_conn():
    """Return a psycopg connection using DATABASE_URL (accepts SQLAlchemy-style URLs)."""
    conn = psycopg.connect(**_CONN_PARAMS)
    try:
        conn.prepare_threshold = 0
    except AttributeError:
        pass
    return conn
