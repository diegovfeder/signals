#!/usr/bin/env python3
"""
Publish Resend templates so they can be used for sending emails
"""
import resend
import os

resend.api_key = os.getenv("RESEND_API_KEY", "re_JH4NQJJY_CjPJe86m7rhiwi1fsJ4TA98L")

template_ids = [
    ("signals-confirmation", "eabb6a15-2d95-4c1d-afa7-944d63cd5b46"),
    ("signals-reactivation", "db0df19d-94fb-46bc-b39c-cd43a2f604c6"),
    ("signals-notification", "2e342d42-8e43-45b6-90b9-c2fa6d8ab573"),
]

print("Publishing templates...\n")

for name, template_id in template_ids:
    try:
        response = resend.Templates.publish(template_id)
        print(f"✅ {name}")
        print(f"   Published: {template_id}")
        print(f"   Response: {response}")
        print()
    except Exception as e:
        print(f"❌ {name} ({template_id})")
        print(f"   Error: {e}")
        print()

print("Done!")
