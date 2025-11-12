"""
Email sending functionality using Resend API.

All emails now use Resend templates stored in frontend/src/lib/email-templates/.
Templates are synced (and published) via: bun run sync-templates:publish
"""

import os
import resend

from .config import settings


# Default configuration
DEFAULT_FROM_EMAIL = "onboarding@resend.dev"
DEFAULT_APP_URL = "http://localhost:3000"


def send_confirmation_email(to_email: str, confirmation_token: str) -> bool:
    """
    Send email confirmation link to new subscriber using Resend template.

    Uses template: signals-confirmation (from frontend/src/lib/email-templates/confirmation.ts)

    Args:
        to_email: Subscriber email address
        confirmation_token: Token for confirmation URL

    Returns:
        True if sent successfully, False otherwise

    Raises:
        RuntimeError: If RESEND_API_KEY is not configured
    """
    api_key = settings.RESEND_API_KEY
    if not api_key:
        raise RuntimeError("RESEND_API_KEY environment variable not set")

    resend.api_key = api_key

    # Build confirmation URL
    from_email = os.getenv("RESEND_FROM_EMAIL", DEFAULT_FROM_EMAIL)
    app_url = os.getenv("APP_BASE_URL", DEFAULT_APP_URL).rstrip("/")
    confirmation_url = f"{app_url}/subscribe/confirm/{confirmation_token}"

    # Send using Resend template (use UUID, not name)
    params = {
        "from": from_email,
        "to": [to_email],
        "template": {
            "id": "eabb6a15-2d95-4c1d-afa7-944d63cd5b46",  # signals-confirmation
            "variables": {
                "CONFIRMATION_URL": confirmation_url,
            },
        },
    }

    try:
        response = resend.Emails.send(params)
        print(
            f"[email] Confirmation email sent to {to_email} (ID: {response.get('id')})"
        )
        return True
    except Exception as exc:
        print(f"[email] Failed to send confirmation email to {to_email}: {exc}")
        return False


def send_reactivation_email(to_email: str, confirmation_token: str) -> bool:
    """
    Send reactivation confirmation link to returning subscriber using Resend template.

    Uses template: signals-reactivation (from frontend/src/lib/email-templates/reactivation.ts)

    Args:
        to_email: Subscriber email address
        confirmation_token: Token for confirmation URL

    Returns:
        True if sent successfully, False otherwise

    Raises:
        RuntimeError: If RESEND_API_KEY is not configured
    """
    api_key = settings.RESEND_API_KEY
    if not api_key:
        raise RuntimeError("RESEND_API_KEY environment variable not set")

    resend.api_key = api_key

    # Build confirmation URL
    from_email = os.getenv("RESEND_FROM_EMAIL", DEFAULT_FROM_EMAIL)
    app_url = os.getenv("APP_BASE_URL", DEFAULT_APP_URL).rstrip("/")
    confirmation_url = f"{app_url}/subscribe/confirm/{confirmation_token}"

    # Send using Resend template (use UUID, not name)
    params = {
        "from": from_email,
        "to": [to_email],
        "template": {
            "id": "db0df19d-94fb-46bc-b39c-cd43a2f604c6",  # signals-reactivation
            "variables": {
                "CONFIRMATION_URL": confirmation_url,
            },
        },
    }

    try:
        response = resend.Emails.send(params)
        print(
            f"[email] Reactivation email sent to {to_email} (ID: {response.get('id')})"
        )
        return True
    except Exception as exc:
        print(f"[email] Failed to send reactivation email to {to_email}: {exc}")
        return False
