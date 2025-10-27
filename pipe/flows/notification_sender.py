"""
Notification Sender Flow

Send email alerts for strong trading signals.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from prefect import flow, task

from tasks.db import get_db_conn
from tasks.email_sending import send_signal_notification
from settings import signal_notify_threshold


@task(name="fetch-strong-signals")
def fetch_strong_signals(min_strength: Optional[float] = None, window_minutes: int = 60) -> List[Dict]:
    """Fetch signals above a strength threshold generated within the last `window_minutes`."""
    threshold = min_strength if min_strength is not None else signal_notify_threshold()
    query = """
        SELECT id, symbol, signal_type, strength, reasoning, price_at_signal, generated_at
        FROM signals
        WHERE strength >= %s
          AND generated_at >= NOW() - %s::interval
        ORDER BY generated_at DESC
    """
    interval = f"{max(window_minutes, 1)} minutes"
    with get_db_conn() as conn, conn.cursor() as cur:
        cur.execute(query, (threshold, interval))
        rows = cur.fetchall()
    signals = []
    for row in rows:
        signal_id, symbol, signal_type, strength, reasoning, price, generated_at = row
        signals.append(
            {
                "id": str(signal_id),
                "symbol": symbol,
                "signal_type": signal_type,
                "strength": float(strength),
                "reasoning": reasoning or [],
                "price": float(price) if price is not None else None,
                "at": generated_at.isoformat() if generated_at else None,
            }
        )
    return signals


@task(name="get-subscribers")
def get_email_subscribers() -> List[Dict]:
    """Return confirmed, active subscribers with their unsubscribe tokens."""
    query = """
        SELECT email, unsubscribe_token
        FROM email_subscribers
        WHERE confirmed = TRUE
          AND (unsubscribed = FALSE OR unsubscribed IS NULL)
    """
    with get_db_conn() as conn, conn.cursor() as cur:
        cur.execute(query)
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
    return sanitized


@task(name="check-rate-limit")
def should_send_email(email: str, signal_id: str, symbol: str) -> bool:
    """
    Enforce rate limiting: max one email per subscriber per symbol per 6 hours.
    """
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
        cur.execute(query, (email, symbol))
        return cur.fetchone() is None


@task(name="send-email")
def send_signal_email(email: str, unsubscribe_token: str, signal: Dict) -> bool:
    """Send the signal email and log it to `sent_notifications` if successful."""
    success = send_signal_notification.fn(email, signal, unsubscribe_token)
    if not success:
        return False

    with get_db_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO sent_notifications (email, signal_id) VALUES (%s, %s)",
            (email, signal["id"]),
        )
        conn.commit()
    return True


@flow(name="notification-sender", log_prints=True)
def notification_sender_flow(min_strength: Optional[float] = None, window_minutes: int = 60):
    """Fetch strong signals, find subscribers, and send notifications."""
    threshold = min_strength if min_strength is not None else signal_notify_threshold()
    print(f"Starting notification sender (min strength: {threshold})...")
    signals = fetch_strong_signals(threshold, window_minutes)
    print(f"Found {len(signals)} strong signals")
    if not signals:
        print("No strong signals to send")
        return

    subscribers = get_email_subscribers()
    print(f"Found {len(subscribers)} active subscribers")
    if not subscribers:
        print("No active subscribers, skipping email send.")
        return

    emails_sent = 0
    for signal in signals:
        for subscriber in subscribers:
            email = subscriber["email"]
            token = subscriber["unsubscribe_token"]
            if should_send_email(email, signal["id"], signal["symbol"]):
                if send_signal_email(email, token, signal):
                    emails_sent += 1

    print(f"✓ Sent {emails_sent} email notifications")


if __name__ == "__main__":
    notification_sender_flow()
