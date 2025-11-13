"""
Notification Dispatcher Flow

Sends email alerts to subscribers for strong trading signals.
Runs after signal_analyzer to notify users of opportunities.
"""

from __future__ import annotations

import argparse
from typing import Any

from prefect import flow, get_run_logger, task

try:
    from tasks.db import get_db_conn
    from tasks.email_sending import send_signal_notification
    from settings import signal_notify_threshold
    from lib.posthog_client import capture_event
except ImportError:
    from pipe.tasks.db import get_db_conn
    from pipe.tasks.email_sending import send_signal_notification
    from pipe.settings import signal_notify_threshold
    from pipe.lib.posthog_client import capture_event


@task(name="fetch-strong-signals")
def fetch_strong_signals(
    min_strength: float | None = None, window_minutes: int = 1440
) -> list[dict[str, Any]]:
    """Fetch signals above a strength threshold generated within the last `window_minutes`."""
    logger = get_run_logger()
    threshold = min_strength if min_strength is not None else signal_notify_threshold()
    logger.info(
        "Fetching strong signals with min_strength=%s window=%d minute(s).",
        threshold,
        window_minutes,
    )
    query = """
        SELECT id, symbol, signal_type, strength, reasoning, price_at_signal, generated_at, explanation
        FROM signals
        WHERE strength >= %s
          AND generated_at >= NOW() - %s::interval
        ORDER BY generated_at DESC
    """
    interval = f"{max(window_minutes, 1)} minutes"
    with get_db_conn() as conn, conn.cursor() as cur:
        cur.execute(query, (threshold, interval), prepare=False)
        rows = cur.fetchall()
    signals: list[dict[str, Any]] = []
    for row in rows:
        (
            signal_id,
            symbol,
            signal_type,
            strength,
            reasoning,
            price,
            generated_at,
            explanation,
        ) = row
        signals.append(
            {
                "id": str(signal_id),
                "symbol": symbol,
                "signal_type": signal_type,
                "strength": float(strength),
                "reasoning": reasoning or [],
                "price": float(price) if price is not None else None,
                "at": generated_at.isoformat() if generated_at else None,
                "explanation": explanation,  # Include explanation from database
            }
        )
    logger.info("Found %d signal(s) meeting strength criteria.", len(signals))
    return signals


@task(name="get-subscribers")
def get_email_subscribers() -> list[dict[str, Any]]:
    """Return confirmed, active subscribers with their unsubscribe tokens."""
    logger = get_run_logger()
    query = """
        SELECT email, unsubscribe_token
        FROM email_subscribers
        WHERE confirmed = TRUE
          AND (unsubscribed = FALSE OR unsubscribed IS NULL)
    """
    with get_db_conn() as conn, conn.cursor() as cur:
        cur.execute(query, prepare=False)
        rows = cur.fetchall()
    sanitized = []
    for email, token in rows:
        clean_email = (email or "").strip().strip('"').strip("'")
        sanitized.append(
            {
                "email": clean_email,
                "unsubscribe_token": token,
            }
        )
    logger.info("Fetched %d active subscriber(s).", len(sanitized))
    return sanitized


@task(name="check-rate-limit")
def should_send_email(email: str, signal_id: str, symbol: str) -> bool:
    """
    Enforce rate limiting: max one email per subscriber per symbol per 6 hours.
    """
    logger = get_run_logger()
    query = """
        SELECT 1
        FROM sent_notifications sn
        JOIN signals s ON sn.signal_id = s.id
        WHERE sn.email = %s
          AND s.symbol = %s
          AND sn.sent_at >= NOW() - INTERVAL '6 hours'
        LIMIT 1
    """
    with get_db_conn() as conn, conn.cursor() as cur:
        cur.execute(query, (email, symbol), prepare=False)
        allowed = cur.fetchone() is None
    if not allowed:
        logger.info(
            "Rate limit prevents sending to %s for symbol %s (signal_id=%s).",
            email,
            symbol,
            signal_id,
        )
    return allowed


@task(name="send-email")
def send_signal_email(
    email: str, unsubscribe_token: str, signal: dict[str, Any]
) -> bool:
    """Send the signal email and log it to `sent_notifications` if successful."""
    logger = get_run_logger()
    success = send_signal_notification.fn(email, signal, unsubscribe_token)
    if not success:
        logger.warning(
            "Failed to send email to %s (signal_id=%s).",
            email,
            signal.get("id"),
        )
        # Log failure to PostHog for observability
        capture_event(
            distinct_id=signal["symbol"],
            event_name="notification_send_failed",
            properties={
                "signal_id": signal.get("id"),
                "symbol": signal["symbol"],
                "email_anonymized": email[:3] + "***" if email else "unknown",
                "signal_type": signal.get("signal_type"),
                "strength": signal.get("strength"),
            },
            groups={"symbol": signal["symbol"]},
        )
        return False

    with get_db_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO sent_notifications (email, signal_id) VALUES (%s, %s)",
            (email, signal["id"]),
            prepare=False,
        )
        conn.commit()
    logger.info(
        "Email sent to %s (signal_id=%s).",
        email,
        signal.get("id"),
    )
    return True


@flow(name="notification-dispatcher", log_prints=True)
def notification_dispatcher_flow(min_strength: float = 60, window_minutes: int = 1440):
    """Fetch strong signals, find subscribers, and send notifications."""
    logger = get_run_logger()
    threshold = min_strength if min_strength is not None else signal_notify_threshold()
    logger.info(
        "Starting notification dispatcher with min_strength=%s window=%d minute(s).",
        threshold,
        window_minutes,
    )
    signals = fetch_strong_signals(threshold, window_minutes)
    logger.info("Evaluating %d strong signal(s) for notification.", len(signals))
    if not signals:
        logger.info("No signals exceeded threshold; exiting dispatcher.")
        return

    subscribers = get_email_subscribers()
    logger.info("Processing %d subscriber(s).", len(subscribers))
    if not subscribers:
        logger.warning("No active subscribers; skipping email notifications.")
        return

    emails_sent = 0
    for signal in signals:
        for subscriber in subscribers:
            email = subscriber["email"]
            token = subscriber["unsubscribe_token"]
            if should_send_email(email, signal["id"], signal["symbol"]):
                if send_signal_email(email, token, signal):
                    emails_sent += 1

    logger.info("Notification dispatcher completed; emails_sent=%d.", emails_sent)


def _parse_cli_args() -> tuple[float | None, int]:
    """Parse CLI arguments for manual dispatcher runs."""
    parser = argparse.ArgumentParser(
        description="Send notification emails for recent strong signals."
    )
    parser.add_argument(
        "--min-strength",
        type=float,
        default=None,
        help="Override strength threshold (default uses SIGNAL_NOTIFY_THRESHOLD).",
    )
    parser.add_argument(
        "--window-minutes",
        type=int,
        default=60,
        help="Lookback window for eligible signals (minutes, default 60).",
    )
    args = parser.parse_args()
    return args.min_strength, args.window_minutes


if __name__ == "__main__":
    cli_min_strength, cli_window = _parse_cli_args()
    notification_dispatcher_flow(
        min_strength=cli_min_strength,
        window_minutes=cli_window,
    )
