"""
Calculate indicators and generate signals from existing market_data.
This bypasses the Yahoo Finance fetch step.
"""
import os
import psycopg
from psycopg.rows import dict_row
import pandas as pd
from datetime import timezone

from data.indicators.rsi import calculate_rsi
from data.utils import calculate_ema
from data.signals.signal_generator import generate_signal
from data.signals.signal_scorer import calculate_signal_strength

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://quantmaster:buysthedip@localhost:5432/signals")

def process_symbol(symbol: str):
    """Calculate indicators and generate signals for a symbol"""
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            # Fetch market data
            cur.execute(
                "SELECT timestamp, close FROM market_data WHERE symbol=%s ORDER BY timestamp ASC",
                (symbol,)
            )
            rows = cur.fetchall()

            if len(rows) < 14:  # Need at least 14 bars for RSI
                print(f"✗ {symbol}: Not enough data ({len(rows)} bars, need 14+)")
                return

            # Build DataFrame
            df = pd.DataFrame([dict(r) for r in rows])
            df["close"] = df["close"].astype(float)

            # Calculate indicators
            rsi_series = calculate_rsi(df, period=14, price_column="close")
            ema12 = calculate_ema(df["close"], span=12)
            ema26 = calculate_ema(df["close"], span=26)

            # Insert indicators for all bars
            indicators_inserted = 0
            for idx in range(len(df)):
                ts = df["timestamp"].iloc[idx]
                rsi_val = float(rsi_series.iloc[idx]) if pd.notna(rsi_series.iloc[idx]) else None
                ema12_val = float(ema12.iloc[idx]) if pd.notna(ema12.iloc[idx]) else None
                ema26_val = float(ema26.iloc[idx]) if pd.notna(ema26.iloc[idx]) else None

                cur.execute(
                    """
                    INSERT INTO indicators (symbol, timestamp, rsi, ema_12, ema_26)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (symbol, timestamp) DO UPDATE
                    SET rsi=EXCLUDED.rsi, ema_12=EXCLUDED.ema_12, ema_26=EXCLUDED.ema_26
                    """,
                    (symbol, ts, rsi_val, ema12_val, ema26_val)
                )
                indicators_inserted += cur.rowcount

            conn.commit()
            print(f"  ✓ Indicators: {indicators_inserted} rows")

            # Generate signal for latest bar
            latest_idx = len(df) - 1
            latest_ts = df["timestamp"].iloc[latest_idx]
            latest_close = float(df["close"].iloc[latest_idx])
            latest_rsi = float(rsi_series.iloc[latest_idx]) if pd.notna(rsi_series.iloc[latest_idx]) else None
            latest_ema12 = float(ema12.iloc[latest_idx]) if pd.notna(ema12.iloc[latest_idx]) else None
            latest_ema26 = float(ema26.iloc[latest_idx]) if pd.notna(ema26.iloc[latest_idx]) else None

            if latest_rsi is None or latest_ema12 is None or latest_ema26 is None:
                print(f"  ✗ Cannot generate signal: missing indicator values")
                return

            # Generate signal
            sig = generate_signal(rsi=latest_rsi, ema_12=latest_ema12, ema_26=latest_ema26, price=latest_close)
            strength = calculate_signal_strength(sig["signal_type"], latest_rsi, None, latest_ema12, latest_ema26)

            rule_version = "rsi_ema_v1"
            idempotency_key = f"{symbol}:{rule_version}:{latest_ts.isoformat()}"
            reasoning_array = sig.get("reasoning", [])

            cur.execute(
                """
                INSERT INTO signals (symbol, timestamp, signal_type, strength, reasoning, price_at_signal, idempotency_key, rule_version)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (idempotency_key) DO NOTHING
                """,
                (symbol, latest_ts, sig["signal_type"], float(strength), reasoning_array, float(latest_close), idempotency_key, rule_version)
            )

            conn.commit()

            print(f"  ✓ Signal: {sig['signal_type']} (strength: {strength:.1f}/100)")
            if strength >= 70:
                print(f"    ⚠️  STRONG SIGNAL: {symbol} {sig['signal_type']} @ ${latest_close:.2f}")

if __name__ == "__main__":
    symbols = ["BTC-USD", "AAPL", "IVV", "BRL=X"]

    print("Calculating indicators and generating signals...\n")

    for symbol in symbols:
        print(f"{symbol}:")
        try:
            process_symbol(symbol)
        except Exception as e:
            print(f"  ✗ Error: {e}")

    print("\n✓ All symbols processed!")

    # Summary
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM indicators")
            indicator_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM signals")
            signal_count = cur.fetchone()[0]

            print(f"\nDatabase summary:")
            print(f"  Indicators: {indicator_count} rows")
            print(f"  Signals: {signal_count} rows")
