"""
Notification Sender Flow

Send email alerts for strong trading signals.
"""

from prefect import flow, task
from typing import List, Dict


@task(name="fetch-strong-signals")
def fetch_strong_signals(min_strength: float = 70.0) -> List[Dict]:
    """
    Fetch recent strong signals from database.

    Args:
        min_strength: Minimum signal strength to send (default: 70)

    Returns:
        List of signal dicts
    """
    # TODO: Implement database query
    # 1. Query signals table
    # 2. Filter by strength >= min_strength
    # 3. Filter by generated_at within last hour
    # 4. Return list of signals

    raise NotImplementedError("Strong signal fetching not yet implemented")


@task(name="get-subscribers")
def get_email_subscribers() -> List[str]:
    """
    Get list of active email subscribers.

    Returns:
        List of email addresses
    """
    # TODO: Implement database query
    # 1. Query email_subscribers table
    # 2. Filter by unsubscribed = false
    # 3. Return list of emails

    raise NotImplementedError("Subscriber fetching not yet implemented")


@task(name="check-rate-limit")
def should_send_email(email: str, signal_id: str) -> bool:
    """
    Check if we should send email (rate limiting).

    Rules:
        - Max 1 email per symbol per 6 hours per user

    Args:
        email: User email
        signal_id: Signal ID

    Returns:
        True if should send, False otherwise
    """
    # TODO: Implement rate limit check
    # 1. Query sent_notifications table
    # 2. Check if email was sent for this symbol in last 6 hours
    # 3. Return boolean

    raise NotImplementedError("Rate limit check not yet implemented")


@task(name="send-email")
def send_signal_email(email: str, signal: Dict):
    """
    Send email notification using Resend.

    Args:
        email: Recipient email
        signal: Signal details dict
    """
    # TODO: Implement email sending
    # 1. Import Resend client
    # 2. Format email template with signal details
    # 3. Send email via Resend API
    # 4. Log to sent_notifications table

    raise NotImplementedError("Email sending not yet implemented")


@flow(name="notification-sender", log_prints=True)
def notification_sender_flow(min_strength: float = 70.0):
    """
    Main flow: Send email notifications for strong signals.

    Args:
        min_strength: Minimum signal strength to notify (default: 70)
    """
    print(f"Starting notification sender (min strength: {min_strength})...")

    # Fetch strong signals
    signals = fetch_strong_signals(min_strength)
    print(f"Found {len(signals)} strong signals")

    if not signals:
        print("No strong signals to send")
        return

    # Get subscribers
    subscribers = get_email_subscribers()
    print(f"Found {len(subscribers)} active subscribers")

    # Send emails
    emails_sent = 0
    for signal in signals:
        for email in subscribers:
            # Check rate limit
            if should_send_email(email, signal['id']):
                send_signal_email(email, signal)
                emails_sent += 1

    print(f"✓ Sent {emails_sent} email notifications")


if __name__ == "__main__":
    notification_sender_flow()
