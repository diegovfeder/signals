"""
Email sending functionality using Resend API.

Handles confirmation emails, reactivation emails, and email templates.
"""

import os
from typing import Optional

import resend

from .config import settings


# Default configuration
DEFAULT_FROM_EMAIL = "onboarding@resend.dev"
DEFAULT_APP_URL = "http://localhost:3000"


def get_confirmation_email_html(confirmation_url: str) -> str:
    """
    Generate HTML template for email confirmation.

    Args:
        confirmation_url: Full URL for email confirmation link

    Returns:
        HTML email content as string
    """
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f3f4f6;">
        <div style="max-width: 560px; margin: 0 auto; padding: 40px 20px;">
            <div style="background: white; border-radius: 8px; padding: 40px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <h1 style="margin: 0 0 24px 0; font-size: 28px; font-weight: 600; color: #111827;">
                    Welcome to Signals!
                </h1>

                <p style="margin: 0 0 24px 0; font-size: 16px; line-height: 1.5; color: #374151;">
                    Thanks for subscribing to automated trading signals. We'll send you notifications when our analysis identifies high-confidence opportunities.
                </p>

                <p style="margin: 0 0 24px 0; font-size: 16px; line-height: 1.5; color: #374151;">
                    Click the button below to confirm your email address:
                </p>

                <div style="text-align: center; margin: 32px 0;">
                    <a href="{confirmation_url}"
                       style="display: inline-block; padding: 14px 28px; background-color: #3b82f6; color: white; text-decoration: none; border-radius: 6px; font-size: 16px; font-weight: 500;">
                        Confirm Email
                    </a>
                </div>

                <div style="margin: 32px 0; padding: 16px; background-color: #f9fafb; border-radius: 6px;">
                    <p style="margin: 0; font-size: 14px; color: #6b7280;">
                        Or copy and paste this link into your browser:
                    </p>
                    <p style="margin: 8px 0 0 0; font-size: 14px; color: #3b82f6; word-break: break-all;">
                        {confirmation_url}
                    </p>
                </div>

                <div style="margin-top: 32px; padding-top: 24px; border-top: 1px solid #e5e7eb;">
                    <p style="margin: 0; font-size: 13px; color: #9ca3af;">
                        If you didn't sign up for Signals, you can safely ignore this email.
                    </p>
                </div>
            </div>

            <div style="text-align: center; margin-top: 24px;">
                <p style="margin: 0; font-size: 13px; color: #6b7280;">
                    Signals - Automated market signals you can actually read
                </p>
            </div>
        </div>
    </body>
    </html>
    """


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
    """
    Generate HTML template for reactivation email.

    Args:
        confirmation_url: Full URL for email confirmation link

    Returns:
        HTML email content as string
    """
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f3f4f6;">
        <div style="max-width: 560px; margin: 0 auto; padding: 40px 20px;">
            <div style="background: white; border-radius: 8px; padding: 40px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <h1 style="margin: 0 0 24px 0; font-size: 28px; font-weight: 600; color: #111827;">
                    Welcome back to Signals!
                </h1>

                <p style="margin: 0 0 24px 0; font-size: 16px; line-height: 1.5; color: #374151;">
                    You're resubscribing to automated trading signals. We'll send you notifications when our analysis identifies high-confidence opportunities.
                </p>

                <p style="margin: 0 0 24px 0; font-size: 16px; line-height: 1.5; color: #374151;">
                    Click the button below to confirm your email address:
                </p>

                <div style="text-align: center; margin: 32px 0;">
                    <a href="{confirmation_url}"
                       style="display: inline-block; padding: 14px 28px; background-color: #3b82f6; color: white; text-decoration: none; border-radius: 6px; font-size: 16px; font-weight: 500;">
                        Confirm Reactivation
                    </a>
                </div>

                <div style="margin: 32px 0; padding: 16px; background-color: #f9fafb; border-radius: 6px;">
                    <p style="margin: 0; font-size: 14px; color: #6b7280;">
                        Or copy and paste this link into your browser:
                    </p>
                    <p style="margin: 8px 0 0 0; font-size: 14px; color: #3b82f6; word-break: break-all;">
                        {confirmation_url}
                    </p>
                </div>

                <div style="margin-top: 32px; padding-top: 24px; border-top: 1px solid #e5e7eb;">
                    <p style="margin: 0; font-size: 13px; color: #9ca3af;">
                        If you didn't request this, you can safely ignore this email.
                    </p>
                </div>
            </div>

            <div style="text-align: center; margin-top: 24px;">
                <p style="margin: 0; font-size: 13px; color: #6b7280;">
                    Signals - Automated market signals you can actually read
                </p>
            </div>
        </div>
    </body>
    </html>
    """


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
    confirmation_url = f"{app_url}/confirm/{confirmation_token}"

    # Build email parameters
    params = {
        "from": from_email,
        "to": [to_email],
        "subject": "Confirm your Signals subscription",
        "html": get_confirmation_email_html(confirmation_url),
        "text": get_confirmation_email_text(confirmation_url),
    }

    try:
        response = resend.Emails.send(params)
        print(f"[email] Confirmation email sent to {to_email} (ID: {response.get('id')})")
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
    confirmation_url = f"{app_url}/confirm/{confirmation_token}"

    # Build email parameters
    params = {
        "from": from_email,
        "to": [to_email],
        "subject": "Welcome back to Signals",
        "html": get_reactivation_email_html(confirmation_url),
        "text": get_reactivation_email_text(confirmation_url),
    }

    try:
        response = resend.Emails.send(params)
        print(f"[email] Reactivation email sent to {to_email} (ID: {response.get('id')})")
        return True
    except Exception as exc:
        print(f"[email] Failed to send reactivation email to {to_email}: {exc}")
        return False
