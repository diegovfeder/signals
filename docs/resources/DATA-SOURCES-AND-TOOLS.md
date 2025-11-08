# Data Sources and Tools

> Quick reference for external data providers and tooling we may evaluate or integrate. Use this when exploring new assets or designing redundancy plans.

---

## 1. Market Data APIs

| Provider | When to Consider | Notes |
| --- | --- | --- |
| **Yahoo Finance** (current) | Default daily OHLCV source (free, no keys). | Already integrated via `pipe/lib/api/yahoo.py`; nightly cadence stays within rate limits. |
| **Twelve Data** | Secondary source for reliability/fallback initiatives. | Account + API key already created. Docs: https://twelvedata.com/docs. Historical guide: https://support.twelvedata.com/en/articles/5214728-getting-historical-data. Free tier limited but flexible. |
| **Tiingo** | Paid REST API with equities/crypto fundamentals. | Useful if we need fundamentals or higher-quality EOD data. https://www.tiingo.com/ |
| **Polygon.io** | High-volume intraday + indicator APIs. | Expensive but offers derived indicators and websockets. https://polygon.io/ |

> Decision tip: keep Yahoo as the source of truth until reliability work is complete; evaluate Twelve Data as the first fallback (see Task Seeds → Provider fallback).

---

## 2. Historical Data Dumps

| Dataset | Scope | Link / Notes |
| --- | --- | --- |
| **Bitcoin Historical Data (Kaggle)** | Multi-year BTC-USD OHLCV at various granularities. | https://www.kaggle.com/datasets/mczielinski/bitcoin-historical-data |
| **Stooq Global EOD** | Daily prices for global equities/indices (CSV). | https://stooq.com/db/h/ — handy for quick experiments or cross-checking Yahoo. |

Use these when seeding backtests offline or validating ingestion logic against an independent dataset.

---

## 3. Analysis & Prototyping Tools

| Tool | Purpose | Link |
| --- | --- | --- |
| **Marimo** | Reactive Python notebooks for experiments + reports. | https://docs.marimo.io/ |
| **Polars** | Columnar DataFrame engine (already used in pipeline). | https://docs.pola.rs/api/python/stable/reference/index.html |
| **Prefect Cloud** | Orchestration / monitoring UI for flows. | https://app.prefect.cloud/ |

Prototype strategy tweaks in Marimo/Polars first; once validated, upstream the logic into `pipe/lib/strategies` or `pipe/lib/indicators` so nightly automation stays consistent.
