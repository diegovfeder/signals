"""
Email Sending Tasks

Sends signal notification emails via Resend using templates.
Template: signals-notification (from frontend/src/lib/email-templates/signal-notification.ts)
"""

from __future__ import annotations

import os
from typing import Dict, List

from dotenv import load_dotenv
from prefect import task
import resend

load_dotenv()

DEFAULT_FROM_EMAIL = "Signals <onboarding@resend.dev>"
DEFAULT_APP_URL = "https://signalsapp.dev"

try:
    from ..lib.explanation_generator import generate_explanation
    from .db import get_db_conn
except ImportError:
    from lib.explanation_generator import generate_explanation
    from tasks.db import get_db_conn


def _maybe_backfill_explanation(signal: Dict) -> str:
    """
    Ensure we have an explanation before sending the email.

    Priority:
        1. Use explanation already present on the signal record.
        2. If ENABLE_LLM_EXPLANATIONS is true, regenerate via LLM,
           persist to the signals table, and return it.
    """
    explanation = signal.get("explanation") or ""
    if explanation:
        _log_explanation_preview(signal.get("id"), explanation)
        print(
            f"[email] Using stored explanation (len={len(explanation)}) "
            f"for signal {signal.get('id')}"
        )
        return explanation

    if os.getenv("ENABLE_LLM_EXPLANATIONS", "false").lower() != "true":
        print(
            f"[email] No stored explanation for {signal.get('id')} "
            "and LLM backfill disabled."
        )
        return ""

    signal_payload = {
        "symbol": signal.get("symbol"),
        "signal_type": signal.get("signal_type"),
        "strength": signal.get("strength"),
        "reasoning": signal.get("reasoning") or [],
        "price": signal.get("price"),
    }

    print(f"[email] Backfilling explanation for signal {signal.get('id')}")
    try:
        explanation = generate_explanation(signal_payload) or ""
    except Exception as exc:
        print(
            f"[email] Exception while generating explanation for {signal.get('id')}: {exc}"
        )
        explanation = ""
    if not explanation:
        print(f"[email] Failed to backfill explanation for {signal.get('id')}")
        return ""

    # Persist the explanation so future sends reuse it.
    signal_id = signal.get("id")
    if signal_id:
        try:
            with get_db_conn() as conn, conn.cursor() as cur:
                cur.execute(
                    "UPDATE signals SET explanation = %s WHERE id = %s",
                    (explanation, signal_id),
                    prepare=False,
                )
                conn.commit()
            print(f"[email] Stored regenerated explanation for signal {signal_id}")
        except Exception as exc:
            print(
                f"[email] Warning: failed to store explanation for {signal_id}: {exc}"
            )

    signal["explanation"] = explanation
    _log_explanation_preview(signal.get("id"), explanation)
    return explanation


def _log_explanation_preview(signal_id: str | None, explanation: str) -> None:
    """Print a trimmed preview so we can confirm what will be sent."""
    preview = (
        (explanation[:160] + "…")
        if len(explanation) > 160
        else explanation or "<<none>>"
    )
    print(f"[email] Explanation preview for {signal_id}: {preview}")


@task(name="send-signal-notification", retries=2, retry_delay_seconds=30)
def send_signal_notification(
    to_email: str, signal: Dict, unsubscribe_token: str
) -> bool:
    """
    Send trading signal notification email using Resend template.

    Uses template: signals-notification (from frontend/src/lib/email-templates/signal-notification.ts)

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

    # Format reasoning for both HTML and text
    reasoning: List[str] = signal.get("reasoning") or []
    reasoning_html = (
        "".join(f"<li>{reason}</li>" for reason in reasoning)
        or "<li>No reasoning provided.</li>"
    )
    reasoning_text = (
        "\n".join(f"- {reason}" for reason in reasoning) or "- No reasoning provided."
    )

    # Format optional explanation (natural language analysis)
    explanation = _maybe_backfill_explanation(signal)
    explanation_text = ""
    explanation_html = ""

    if explanation:
        # Split into paragraphs (max 2)
        paragraphs = [p.strip() for p in explanation.split("\n\n") if p.strip()][:2]
        explanation_text = "\n\n".join(paragraphs)
        explanation_html = "".join(
            f"<p style='margin: 0 0 12px 0;'>{p}</p>" for p in paragraphs
        )
        print(
            f"[email] Explanation text ready for {signal.get('id')} "
            f"(len={len(explanation_text)})"
        )
    else:
        print(f"[email] No explanation available for {signal.get('id')}")

    # Send using Resend template (use UUID, not name)
    params = {
        "from": from_email,
        "to": [to_email],
        "template": {
            "id": "2e342d42-8e43-45b6-90b9-c2fa6d8ab573",  # signals-notification
            "variables": {
                "SYMBOL": signal.get("symbol", "ASSET"),
                "SIGNAL_TYPE": signal.get("signal_type", "HOLD"),
                "STRENGTH": round(signal.get("strength", 0)),  # Number type for Resend
                "PRICE": f"{float(signal.get('price', 0)):,.2f}",
                "TIMESTAMP": str(signal.get("at") or signal.get("timestamp") or "now"),
                "REASONING_HTML": reasoning_html,
                "REASONING_TEXT": reasoning_text,
                "EXPLANATION_HTML": explanation_html,
                "EXPLANATION_TEXT": explanation_text,
                "UNSUBSCRIBE_URL": unsubscribe_url,
            },
        },
    }

    try:
        resend.Emails.send(params)
        return True
    except Exception as exc:
        print(f"[email] Failed to send signal email to {to_email}: {exc}")
        return False
