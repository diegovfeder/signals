#!/usr/bin/env python3
"""
Simple test script to send email with Resend template
"""
import resend
import os

# Set API key
resend.api_key = os.getenv("RESEND_API_KEY", "re_JH4NQJJY_CjPJe86m7rhiwi1fsJ4TA98L")

print("=" * 60)
print("Testing Resend Template Email Sending")
print("=" * 60)

# Test: Send with template UUID to verified email
print("\nSending test email with template UUID...")
try:
    params = {
        "from": "Signals <onboarding@resend.dev>",
        "to": ["diegovfeder@gmail.com"],  # Use your verified email
        "template": {
            "id": "eabb6a15-2d95-4c1d-afa7-944d63cd5b46",
            "variables": {
                "CONFIRMATION_URL": "http://localhost:3000/subscribe/confirm/test-token-123",
            },
        },
    }
    response = resend.Emails.send(params)
    print(f"✅ Email sent successfully!")
    print(f"   Email ID: {response.get('id')}")
    print(f"   Full response: {response}")
    print("\n📧 Check your inbox at diegovfeder@gmail.com")
except Exception as e:
    print(f"❌ Failed: {e}")

print("\n" + "=" * 60)
