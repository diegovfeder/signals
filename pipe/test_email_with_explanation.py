#!/usr/bin/env python3
"""Test signal email sending path with optional explanation backfill."""

from __future__ import annotations

import argparse
import os

from tasks.email_sending import send_signal_notification


def build_sample_signal() -> dict:
    return {
        "id": "3c20256d-b4c6-4c11-9b61-71ce5502bb33",
        "symbol": "BTC-USD",
        "signal_type": "BUY",
        "strength": 85.5,
        "reasoning": [
            "MACD histogram showing strong bullish momentum",
            "EMA fast crossed above EMA slow",
            "RSI at 38 indicates room to run",
        ],
        "price": 102500.00,
        "at": "2025-11-12T23:21:00+00:00",
        "explanation": (
            "Bitcoin is showing strong bullish momentum with a MACD histogram surge"
            " indicating growing buying pressure. The fast exponential moving"
            " average has crossed above the slow EMA, a classic technical signal"
            " that suggests the start of an uptrend. This crossover pattern"
            " historically precedes significant price appreciation.\n\nWith the"
            " RSI indicator at 38, Bitcoin is not yet overbought, meaning there"
            " is substantial room for the rally to continue before hitting"
            " resistance levels. This combination of momentum indicators and"
            " positioning suggests a favorable entry point for long positions,"
            " though investors should always manage risk appropriately with"
            " stop-loss orders."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send a sample signal email using the Prefect task",
    )
    parser.add_argument(
        "--to",
        dest="to_email",
        default=os.getenv("RESEND_TEST_EMAIL"),
        help="Recipient email (or set RESEND_TEST_EMAIL)",
    )
    parser.add_argument(
        "--unsubscribe-token",
        default="test-token-123",
        help="Token used for unsubscribe link generation",
    )
    parser.add_argument(
        "--strip-explanation",
        action="store_true",
        help="Send without pre-filled explanation so LLM backfill can run",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.to_email:
        print("❌ Provide a recipient via --to or RESEND_TEST_EMAIL")
        return 1

    signal = build_sample_signal()
    if args.strip_explanation:
        signal.pop("explanation", None)

    print("Testing email with explanation...")
    print(f"Signal explanation length: {len(signal.get('explanation') or '')} chars")
    preview = (signal.get("explanation") or "")[:100]
    print(f"Signal explanation preview: {preview}...")

    result = send_signal_notification.fn(  # Call the underlying task function
        to_email=args.to_email,
        signal=signal,
        unsubscribe_token=args.unsubscribe_token,
    )

    print(f"\nResult: {'✅ Success' if result else '❌ Failed'}")
    return 0 if result else 2


if __name__ == "__main__":
    raise SystemExit(main())
