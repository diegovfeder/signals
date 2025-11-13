"""Database utilities for the strategy lab."""

from __future__ import annotations

import os
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator

import polars as pl
import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

# Ensure environment is loaded - check lab/.env first, then pipe/.env
from dotenv import load_dotenv

_LAB_ENV = Path(__file__).parent.parent / ".env"
_PIPE_ENV = Path(__file__).parent.parent.parent / "pipe" / ".env"

if _LAB_ENV.exists():
    load_dotenv(_LAB_ENV, override=False)
elif _PIPE_ENV.exists():
    load_dotenv(_PIPE_ENV, override=False)
else:
    import warnings
    warnings.warn(
        "No .env file found. Copy lab/.env.example to lab/.env and configure it.",
        RuntimeWarning
    )


_POOL: ConnectionPool | None = None


def _normalize_dsn(dsn: str) -> str:
    """Ensure the DSN uses a psycopg-compatible prefix."""

    return dsn.replace("postgresql+psycopg://", "postgresql://")


def _database_url() -> str:
    try:
        url = os.environ["DATABASE_URL"]
    except KeyError as exc:
        raise RuntimeError("DATABASE_URL environment variable is required") from exc
    return _normalize_dsn(url)


def get_pool() -> ConnectionPool:
    """Return a shared psycopg connection pool."""

    global _POOL
    if _POOL is None:
        _POOL = ConnectionPool(conninfo=_database_url(), kwargs={"autocommit": False})
    return _POOL


@contextmanager
def get_connection() -> Iterator[psycopg.Connection]:
    """Context manager yielding a psycopg connection from the pool."""

    pool = get_pool()
    with pool.connection() as conn:  # type: ignore[assignment]
        yield conn


def list_symbols() -> list[str]:
    """Return the set of active symbols available in the database."""

    with get_connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "SELECT symbol FROM symbols WHERE active = true ORDER BY symbol"
        )
        rows = cur.fetchall()
    return [row["symbol"] for row in rows]


def fetch_price_history(
    symbol: str,
    *,
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int | None = None,
) -> pl.DataFrame:
    """Fetch OHLCV and indicator history for a symbol as a Polars DataFrame."""

    params: list[object] = [symbol]
    filters = ["m.symbol = %s"]

    if start is not None:
        filters.append("m.timestamp >= %s")
        params.append(start)
    if end is not None:
        filters.append("m.timestamp <= %s")
        params.append(end)

    columns = (
        "m.symbol",
        "m.timestamp",
        "m.open",
        "m.high",
        "m.low",
        "m.close",
        "m.volume",
        "i.rsi",
        "i.ema_12",
        "i.ema_26",
        "i.macd_histogram",
    )
    select = ", ".join(columns)

    query = (
        "SELECT "
        f"{select} "
        "FROM market_data AS m "
        "LEFT JOIN indicators AS i ON i.symbol = m.symbol AND i.timestamp = m.timestamp "
        "WHERE "
        + " AND ".join(filters)
        + " ORDER BY m.timestamp ASC"
    )

    if limit is not None:
        query += " LIMIT %s"
        params.append(limit)

    with get_connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, params)
        rows = cur.fetchall()

    if not rows:
        return pl.DataFrame(
            schema={
                "symbol": pl.Utf8,
                "timestamp": pl.Datetime,
                "open": pl.Float64,
                "high": pl.Float64,
                "low": pl.Float64,
                "close": pl.Float64,
                "volume": pl.Int64,
                "rsi": pl.Float64,
                "ema_fast": pl.Float64,
                "ema_slow": pl.Float64,
                "macd_hist": pl.Float64,
            }
        )

    frame = pl.from_dicts(rows)
    return frame.rename(
        {
            "symbol": "symbol",
            "timestamp": "timestamp",
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "volume": "volume",
            "rsi": "rsi",
            "ema_12": "ema_fast",
            "ema_26": "ema_slow",
            "macd_histogram": "macd_hist",
        }
    )
