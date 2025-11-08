"""
Email sending functionality using Resend API.

Handles confirmation emails, reactivation emails, and email templates.
"""

import os
import resend

from .config import settings

EmailSendParams = resend.Emails.SendParams


# Default configuration
DEFAULT_FROM_EMAIL = "onboarding@resend.dev"
DEFAULT_APP_URL = "http://localhost:3000"


EMAIL_THEME = {
    "background": "#05090a",
    "card": "#0f1512",
    "card_border": "#1b2b23",
    "divider": "#1f3128",
    "badge_bg": "#13231b",
    "badge_text": "#7ef2bf",
    "text_primary": "#e2e8f0",
    "text_secondary": "#9da7b3",
    "muted": "#7b8a83",
    "primary": "#0c8f58",
    "button_shadow": "0 12px 30px rgba(20, 184, 124, 0.25)",
}


def build_email_html(
    *,
    eyebrow: str,
    title: str,
    intro: str,
    message_lines: list[str],
    button_label: str,
    confirmation_url: str,
    footnote: str,
    highlight_label: str | None = None,
    highlight_body: str | None = None,
) -> str:
    """Build a Signals-branded HTML email with consistent styling."""

    message_html = "".join(
        f"""
        <p style=\"margin: 0 0 16px 0; font-size: 15px; line-height: 1.6; color: {EMAIL_THEME["text_secondary"]};\">
            {line}
        </p>
        """
        for line in message_lines
    )

    highlight_html = ""
    if highlight_label and highlight_body:
        highlight_html = f"""
        <div style=\"margin: 24px 0; padding: 16px 18px; border-radius: 12px; background: {EMAIL_THEME["badge_bg"]}; border: 1px solid {EMAIL_THEME["divider"]};\">
            <p style=\"margin: 0; font-size: 13px; letter-spacing: 0.08em; text-transform: uppercase; color: {EMAIL_THEME["muted"]};\">{highlight_label}</p>
            <p style=\"margin: 6px 0 0 0; font-size: 15px; color: {EMAIL_THEME["text_primary"]}; font-weight: 500;\">{highlight_body}</p>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html lang=\"en\">
    <head>
        <meta charset=\"utf-8\">
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    </head>
    <body style=\"margin: 0; padding: 32px 16px; background: {EMAIL_THEME["background"]}; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;\">
        <table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\" width=\"100%\" style=\"max-width: 600px; margin: 0 auto;\">
            <tr>
                <td>
                    <div style=\"background: {EMAIL_THEME["card"]}; border: 1px solid {EMAIL_THEME["card_border"]}; border-radius: 24px; padding: 40px; box-shadow: 0 20px 60px rgba(3, 7, 5, 0.55);\">
                        <p style=\"margin: 0 0 20px 0; display: inline-block; padding: 6px 12px; font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase; color: {EMAIL_THEME["badge_text"]}; background: {EMAIL_THEME["badge_bg"]}; border-radius: 999px; border: 1px solid {EMAIL_THEME["divider"]};\">{eyebrow}</p>
                        <h1 style=\"margin: 0 0 12px 0; font-size: 28px; color: {EMAIL_THEME["text_primary"]};\">{title}</h1>
                        <p style=\"margin: 0 0 18px 0; font-size: 16px; line-height: 1.6; color: {EMAIL_THEME["text_primary"]};\">{intro}</p>
                        {message_html}
                        {highlight_html}
                        <div style=\"text-align: center; margin: 32px 0;\">
                            <a href=\"{confirmation_url}\" style=\"display: inline-block; padding: 14px 32px; border-radius: 999px; background-image: linear-gradient(120deg, #00f5a0, {EMAIL_THEME["primary"]}); color: #031a12; font-weight: 600; font-size: 16px; text-decoration: none; box-shadow: {EMAIL_THEME["button_shadow"]};\">
                                {button_label}
                            </a>
                        </div>
                        <p style=\"margin: 0 0 8px 0; font-size: 13px; color: {EMAIL_THEME["muted"]}; text-align: center;\">Can't click the button?</p>
                        <p style=\"margin: 0; font-size: 13px; color: {EMAIL_THEME["text_secondary"]}; word-break: break-all; text-align: center;\">
                            <a href=\"{confirmation_url}\" style=\"color: {EMAIL_THEME["badge_text"]}; text-decoration: none;\">{confirmation_url}</a>
                        </p>
                        <div style=\"margin-top: 36px; padding-top: 24px; border-top: 1px solid {EMAIL_THEME["divider"]};\">
                            <p style=\"margin: 0; font-size: 13px; color: {EMAIL_THEME["text_secondary"]};\">{footnote}</p>
                        </div>
                    </div>
                    <p style=\"margin: 24px 0 0 0; font-size: 12px; text-align: center; color: {EMAIL_THEME["muted"]};\">Signals · Automated market signals you can actually read</p>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


def get_confirmation_email_html(confirmation_url: str) -> str:
    """Branded confirmation email for new subscribers."""

    return build_email_html(
        eyebrow="Signals",
        title="Welcome to Signals",
        intro="You're almost ready to receive automated trading intelligence the moment it ships.",
        message_lines=[
            "Confirming your email tells us we can securely deliver market-ready signals straight to your inbox.",
            "Hit confirm and we'll activate notifications aligned with your dashboard preferences.",
        ],
        button_label="Confirm email",
        confirmation_url=confirmation_url,
        footnote="If you didn't sign up for Signals, you can safely ignore this email.",
        highlight_label="Status",
        highlight_body="Awaiting confirmation — link valid for 48 hours",
    )


def get_confirmation_email_text(confirmation_url: str) -> str:
    """
    Generate plain text template for email confirmation.

    Args:
        confirmation_url: Full URL for email confirmation link

    Returns:
        Plain text email content
    """
    return f"""Welcome to Signals!

Thanks for subscribing to automated trading signals. We'll send you notifications when our analysis identifies high-confidence opportunities.

Click this link to confirm your email address:
{confirmation_url}

If you didn't sign up for Signals, you can safely ignore this email.

---
Signals - Automated market signals you can actually read
"""


def get_reactivation_email_html(confirmation_url: str) -> str:
    """Branded reactivation email for returning subscribers."""

    return build_email_html(
        eyebrow="Signals",
        title="Welcome back to Signals",
        intro="We saved your signal preferences. Reactivate to resume curated alerts with zero onboarding friction.",
        message_lines=[
            "Reconfirming verifies that we can resume delivery of the watchlists and guardrails you configured.",
            "Loved something in the dashboard recently? Reactivation keeps your notifications in sync.",
        ],
        button_label="Confirm reactivation",
        confirmation_url=confirmation_url,
        footnote="If you didn't request this, you can safely ignore this email.",
        highlight_label="Status",
        highlight_body="Reactivation pending — link valid for 48 hours",
    )


def get_reactivation_email_text(confirmation_url: str) -> str:
    """
    Generate plain text template for reactivation email.

    Args:
        confirmation_url: Full URL for email confirmation link

    Returns:
        Plain text email content
    """
    return f"""Welcome back to Signals!

You're resubscribing to automated trading signals. We'll send you notifications when our analysis identifies high-confidence opportunities.

Click this link to confirm your email address:
{confirmation_url}

If you didn't request this, you can safely ignore this email.

---
Signals - Automated market signals you can actually read
"""


def send_confirmation_email(to_email: str, confirmation_token: str) -> bool:
    """
    Send email confirmation link to new subscriber.

    Args:
        to_email: Subscriber email address
        confirmation_token: Token for confirmation URL

    Returns:
        True if sent successfully, False otherwise

    Raises:
        RuntimeError: If RESEND_API_KEY is not configured
    """
    # Get Resend API key from settings (loaded from .env)
    api_key = settings.RESEND_API_KEY
    if not api_key:
        raise RuntimeError("RESEND_API_KEY environment variable not set")

    resend.api_key = api_key

    # Get configuration
    from_email = os.getenv("RESEND_FROM_EMAIL", DEFAULT_FROM_EMAIL)
    app_url = os.getenv("APP_BASE_URL", DEFAULT_APP_URL).rstrip("/")
    confirmation_url = f"{app_url}/subscribe/confirm/{confirmation_token}"

    # Build email parameters
    params: EmailSendParams = {
        "from": from_email,
        "to": [to_email],
        "subject": "Confirm your Signals subscription",
        "html": get_confirmation_email_html(confirmation_url),
        "text": get_confirmation_email_text(confirmation_url),
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
    Send reactivation confirmation link to returning subscriber.

    Args:
        to_email: Subscriber email address
        confirmation_token: Token for confirmation URL

    Returns:
        True if sent successfully, False otherwise

    Raises:
        RuntimeError: If RESEND_API_KEY is not configured
    """
    # Get Resend API key from settings (loaded from .env)
    api_key = settings.RESEND_API_KEY
    if not api_key:
        raise RuntimeError("RESEND_API_KEY environment variable not set")

    resend.api_key = api_key

    # Get configuration
    from_email = os.getenv("RESEND_FROM_EMAIL", DEFAULT_FROM_EMAIL)
    app_url = os.getenv("APP_BASE_URL", DEFAULT_APP_URL).rstrip("/")
    confirmation_url = f"{app_url}/subscribe/confirm/{confirmation_token}"

    # Build email parameters
    params: EmailSendParams = {
        "from": from_email,
        "to": [to_email],
        "subject": "Welcome back to Signals",
        "html": get_reactivation_email_html(confirmation_url),
        "text": get_reactivation_email_text(confirmation_url),
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
