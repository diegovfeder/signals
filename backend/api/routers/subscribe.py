"""
Email Subscription Router

Endpoints for managing email subscriptions.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import EmailSubscriber
from ..schemas import EmailSubscribeRequest, EmailSubscribeResponse
import secrets

router = APIRouter()


@router.post("/", response_model=EmailSubscribeResponse)
async def subscribe_email(
    request: EmailSubscribeRequest,
    db: Session = Depends(get_db)
):
    """
    Subscribe an email address to receive signal notifications.

    Request Body:
        - email: Valid email address

    Returns:
        Success message with email confirmation

    Raises:
        400: Email already subscribed
        422: Invalid email format
    """
    # Check if email already exists
    existing = db.query(EmailSubscriber)\
        .filter(EmailSubscriber.email == request.email)\
        .first()
    
    if existing:
        if existing.unsubscribed:
            # Reactivate subscription
            existing.unsubscribed = False
            existing.confirmed = False
            existing.confirmation_token = secrets.token_urlsafe(32)
            db.commit()
            # TODO Phase 2: Send confirmation email via Resend
            return EmailSubscribeResponse(
                message="Subscription reactivated. Please check your email for confirmation.",
                email=request.email
            )
        else:
            return EmailSubscribeResponse(
                message="Email already subscribed",
                email=request.email
            )
    
    # Create new subscriber with confirmation token
    confirmation_token = secrets.token_urlsafe(32)
    unsubscribe_token = secrets.token_urlsafe(32)
    
    subscriber = EmailSubscriber(
        email=request.email,
        confirmed=False,
        confirmation_token=confirmation_token,
        unsubscribe_token=unsubscribe_token
    )
    
    db.add(subscriber)
    db.commit()
    
    # TODO Phase 2: Send confirmation email via Resend
    # Email should contain link: /api/subscribe/confirm/{confirmation_token}
    
    return EmailSubscribeResponse(
        message="Subscription pending confirmation. Please check your email.",
        email=request.email
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
