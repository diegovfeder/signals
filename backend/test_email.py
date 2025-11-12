#!/usr/bin/env python3

"""Manual test helper for sending Resend template emails.

The script intentionally requires real credentials via environment variables so
secrets never live in source control. Usage:

    RESEND_API_KEY=... python backend/test_email.py --to you@example.com

Optionally set --template-id, --confirmation-url, and --from-email. Defaults
match the production confirmation template.
"""

from __future__ import annotations

import argparse
import os
import sys

import resend

DEFAULT_TEMPLATE_ID = "eabb6a15-2d95-4c1d-afa7-944d63cd5b46"
DEFAULT_CONFIRMATION_URL = (
    "http://localhost:3000/subscribe/confirm/test-token-123"
)
DEFAULT_FROM_EMAIL = "Signals <onboarding@resend.dev>"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send test email via Resend template")
    parser.add_argument(
        "--to",
        dest="to_email",
        default=os.getenv("RESEND_TEST_EMAIL"),
        help="Recipient email (or set RESEND_TEST_EMAIL)",
    )
    parser.add_argument(
        "--template-id",
        default=os.getenv("RESEND_TEMPLATE_ID", DEFAULT_TEMPLATE_ID),
        help="Resend template ID to use (defaults to confirmation template)",
    )
    parser.add_argument(
        "--confirmation-url",
        default=os.getenv("TEST_CONFIRMATION_URL", DEFAULT_CONFIRMATION_URL),
        help="Confirmation URL injected into the template variables",
    )
    parser.add_argument(
        "--from-email",
        default=os.getenv("RESEND_FROM_EMAIL", DEFAULT_FROM_EMAIL),
        help="From header used when sending the test email",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    api_key = os.getenv("RESEND_API_KEY")
    if not api_key:
        print("❌ RESEND_API_KEY is required to send a test email", file=sys.stderr)
        return 1
    if not args.to_email:
        print(
            "❌ Provide a recipient via --to or RESEND_TEST_EMAIL",
            file=sys.stderr,
        )
        return 1

    resend.api_key = api_key
    print("=" * 60)
    print("Testing Resend Template Email Sending")
    print("=" * 60)

    params = {
        "from": args.from_email,
        "to": [args.to_email],
        "template": {
            "id": args.template_id,
            "variables": {
                "CONFIRMATION_URL": args.confirmation_url,
            },
        },
    }

    print(f"\nSending test email to {args.to_email} using template {args.template_id}...")
    try:
        response = resend.Emails.send(params)
        print("✅ Email sent successfully!")
        print(f"   Email ID: {response.get('id')}")
        print(f"   Full response: {response}")
        return 0
    except Exception as exc:  # noqa: BLE001 printing manual test failure
        print(f"❌ Failed: {exc}")
        return 2
    finally:
        print("\n" + "=" * 60)


if __name__ == "__main__":
    raise SystemExit(main())
