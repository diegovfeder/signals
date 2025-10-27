"""
Email Sending Tasks

Utilities for sending emails via Resend.
"""

from __future__ import annotations

import os
from typing import Dict, List

from dotenv import load_dotenv
from prefect import task
import resend

load_dotenv()

DEFAULT_FROM_EMAIL = "Signals Bot <alerts@resend.dev>"
DEFAULT_APP_URL = "https://signalsapp.dev"


@task(name="send-signal-notification", retries=2, retry_delay_seconds=30)
def send_signal_notification(
    to_email: str,
    signal: Dict,
    unsubscribe_token: str
) -> bool:
    """
    Send trading signal notification email.

    Args:
        to_email: Recipient email address
        signal: Signal details dict (symbol, type, strength, reasoning, price, at)
        unsubscribe_token: Token for unsubscribe link

    Returns:
        True if sent successfully, False otherwise
    """
    api_key = os.getenv("RESEND_API_KEY")
    if not api_key:
        raise RuntimeError("RESEND_API_KEY not set; cannot send emails via Resend.")
    resend.api_key = api_key

    from_email = os.getenv("RESEND_FROM_EMAIL", DEFAULT_FROM_EMAIL)
    app_url = os.getenv("APP_BASE_URL", DEFAULT_APP_URL).rstrip("/")
    unsubscribe_url = f"{app_url}/unsubscribe/{unsubscribe_token}"

    html_body = format_signal_email_html(signal, unsubscribe_url)
    text_body = format_signal_email_text(signal, unsubscribe_url)

    params = {
        "from": from_email,
        "to": [to_email],
        "subject": f"{signal.get('symbol', 'Asset')} Signal: {signal.get('signal_type', 'HOLD')}",
        "html": html_body,
        "text": text_body,
    }

    try:
        resend.Emails.send(params)
        return True
    except Exception as exc:  # Resend raises generic Exception subclasses
        print(f"[email] Failed to send signal email to {to_email}: {exc}")
        return False


def format_signal_email_html(signal: Dict, unsubscribe_url: str) -> str:
    """
    Format signal notification email as HTML.
    """
    symbol = signal.get("symbol", "Unknown")
    signal_type = signal.get("signal_type", "HOLD")
    strength = signal.get("strength", 0)
    price = signal.get("price", 0)
    timestamp = signal.get("at") or signal.get("timestamp")
    reasoning = signal.get("reasoning") or []

    reasoning_html = "".join(
        f"<li>{reason}</li>" for reason in reasoning
    ) or "<li>No reasoning provided.</li>"

    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 560px; margin: 0 auto; color: #0f172a;">
      <h2 style="margin-bottom: 8px;">New {signal_type} signal for {symbol}</h2>
      <p style="margin: 0; color: #475569;">Generated at {timestamp or 'now'}</p>
      <div style="margin: 24px 0; padding: 16px; border: 1px solid #e2e8f0; border-radius: 8px;">
        <p style="font-size: 32px; margin: 0; font-weight: bold;">{signal_type}</p>
        <p style="margin: 8px 0;">Strength: <strong>{round(strength)} / 100</strong></p>
        <p style="margin: 8px 0;">Price at signal: <strong>${float(price):,.2f}</strong></p>
      </div>
      <div style="margin-bottom: 24px;">
        <p style="margin-bottom: 8px; font-weight: bold;">Reasoning</p>
        <ul style="margin: 0 0 16px 20px; padding: 0; color: #334155;">
          {reasoning_html}
        </ul>
      </div>
      <p style="font-size: 12px; color: #94a3b8;">
        Don't want these emails? <a href="{unsubscribe_url}">Unsubscribe</a>.
      </p>
    </div>
    """


def format_signal_email_text(signal: Dict, unsubscribe_url: str) -> str:
    """
    Plain-text fallback for the signal notification email.
    """
    symbol = signal.get("symbol", "Unknown")
    signal_type = signal.get("signal_type", "HOLD")
    strength = signal.get("strength", 0)
    price = signal.get("price", 0)
    timestamp = signal.get("at") or signal.get("timestamp")
    reasoning: List[str] = signal.get("reasoning") or []

    reasoning_lines = "\n".join(f"- {reason}" for reason in reasoning) or "- No reasoning provided."

    return (
        f"New {signal_type} signal for {symbol}\n"
        f"Generated at: {timestamp or 'now'}\n"
        f"Strength: {round(strength)} / 100\n"
        f"Price at signal: ${float(price):,.2f}\n\n"
        f"Reasoning:\n{reasoning_lines}\n\n"
        f"Unsubscribe: {unsubscribe_url}"
    )
