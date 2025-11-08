"""
Email Subscription Router

Endpoints for managing email subscriptions.
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from slowapi import Limiter
from slowapi.util import get_remote_address
from ..database import get_db
from ..models import EmailSubscriber
from ..schemas import (
    EmailSubscribeRequest,
    EmailSubscribeResponse,
    EmailSubscriberListResponse,
    EmailSubscriberSummary,
    )
from ..email import send_confirmation_email, send_reactivation_email
import secrets

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


def _normalize_email(raw_email: str) -> str:
    """Strip whitespace and quotes, lower-case the email for uniqueness."""
    return raw_email.strip().strip('"').lower()


@router.get("", response_model=EmailSubscriberListResponse)
@router.get("/", response_model=EmailSubscriberListResponse, include_in_schema=False)
@limiter.limit("60/minute")
async def list_subscribers(
    request: Request,
    include_unsubscribed: bool = True,
    include_tokens: bool = False,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    List subscribers for internal dashboards.

    Query params:
        - include_unsubscribed: include unsubscribed emails (default True).
        - include_tokens: surface confirmation/unsubscribe tokens (default False).
        - limit / offset: pagination controls (max limit 500).
    """
    base_query = db.query(EmailSubscriber)
    if not include_unsubscribed:
        base_query = base_query.filter(EmailSubscriber.unsubscribed.is_(False))

    total = base_query.count()
    rows = (
        base_query.order_by(EmailSubscriber.subscribed_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    summaries = []
    for row in rows:
        email_value = (
            row.email.strip().strip('"') if isinstance(row.email, str) else row.email
        )
        confirmation_value = (
            row.confirmation_token.strip('"')
            if include_tokens and isinstance(row.confirmation_token, str)
            else (row.confirmation_token if include_tokens else None)
        )
        unsubscribe_value = (
            row.unsubscribe_token.strip('"')
            if include_tokens and isinstance(row.unsubscribe_token, str)
            else (row.unsubscribe_token if include_tokens else None)
        )
        summaries.append(
            EmailSubscriberSummary(
                email=email_value,
                subscribed_at=row.subscribed_at,
                confirmed=row.confirmed,
                confirmed_at=row.confirmed_at,
                unsubscribed=row.unsubscribed,
                confirmation_token=confirmation_value,
                unsubscribe_token=unsubscribe_value,
            )
        )

    return EmailSubscriberListResponse(subscribers=summaries, total=total)


@router.post("", response_model=EmailSubscribeResponse)
@router.post("/", response_model=EmailSubscribeResponse, include_in_schema=False)
@limiter.limit("5/minute")
async def subscribe_email(
    request: Request,
    body: EmailSubscribeRequest,
    db: Session = Depends(get_db)
):
    """
    Subscribe an email address to receive signal notifications.

    Request Body:
        - email: Valid email address

    Returns:
        Success message with email confirmation

    Raises:
        409: Email already subscribed
        422: Invalid email format
    """
    normalized_email = _normalize_email(body.email)

    # Check if email already exists
    existing = db.query(EmailSubscriber)\
        .filter(func.lower(EmailSubscriber.email) == normalized_email)\
        .first()
    
    if existing:
        if existing.unsubscribed:
            # Reactivate subscription
            existing.unsubscribed = False
            existing.confirmed = False
            existing.confirmation_token = secrets.token_urlsafe(32)
            existing.email = normalized_email
            db.commit()

            # Send reactivation confirmation email
            try:
                send_reactivation_email(existing.email, existing.confirmation_token)
            except Exception as e:
                print(f"[subscribe] Failed to send reactivation email: {e}")
                # Don't fail the request - subscriber is reactivated, email is best-effort

            return EmailSubscribeResponse(
                message="Subscription reactivated. Please check your email for confirmation.",
                email=body.email
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already subscribed",
        )
    
    # Create new subscriber with confirmation token
    confirmation_token = secrets.token_urlsafe(32)
    unsubscribe_token = secrets.token_urlsafe(32)
    
    subscriber = EmailSubscriber(
        email=normalized_email,
        confirmed=False,
        confirmation_token=confirmation_token,
        unsubscribe_token=unsubscribe_token
    )
    
    db.add(subscriber)
    db.commit()

    # Send confirmation email
    try:
        send_confirmation_email(subscriber.email, subscriber.confirmation_token)
    except Exception as e:
        print(f"[subscribe] Failed to send confirmation email: {e}")
        # Don't fail the request - subscriber is created, email is best-effort

    return EmailSubscribeResponse(
        message="Subscription pending confirmation. Please check your email.",
        email=body.email
    )


@router.post("/unsubscribe/{token}")
async def unsubscribe_email(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Unsubscribe from email notifications using unsubscribe token.

    Path Parameters:
        - token: Unsubscribe token from email

    Returns:
        Success message

    Raises:
        404: Invalid token
    """
    # Find subscriber by unsubscribe_token
    subscriber = db.query(EmailSubscriber)\
        .filter(EmailSubscriber.unsubscribe_token == token)\
        .first()
    
    if not subscriber:
        raise HTTPException(
            status_code=404,
            detail="Invalid unsubscribe token"
        )
    
    # Set unsubscribed flag
    subscriber.unsubscribed = True
    db.commit()

    return {
        "message": "Successfully unsubscribed from trading signals",
        "email": subscriber.email
    }


@router.get("/confirm/{token}")
@limiter.limit("20/minute")
async def confirm_email(
    request: Request,
    token: str,
    db: Session = Depends(get_db)
):
    """
    Confirm email subscription using confirmation token from email link.

    Path Parameters:
        - token: Confirmation token from email

    Returns:
        Success message with email address

    Raises:
        404: Invalid or already used confirmation token
    """
    # Find subscriber by confirmation_token
    subscriber = db.query(EmailSubscriber)\
        .filter(EmailSubscriber.confirmation_token == token)\
        .filter(EmailSubscriber.confirmed == False)\
        .first()

    if not subscriber:
        raise HTTPException(
            status_code=404,
            detail="Invalid or already used confirmation token"
        )

    # Mark as confirmed
    subscriber.confirmed = True
    subscriber.confirmed_at = datetime.now()
    db.commit()

    return {
        "message": "Email confirmed! You'll now receive trading signals.",
        "email": subscriber.email
    }
