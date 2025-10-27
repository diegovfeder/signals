"""
Pydantic Schemas

Request and response models for API validation.
"""

from pydantic import BaseModel, EmailStr, Field, field_serializer
from typing import List, Literal
from datetime import datetime
from uuid import UUID

# Signal Types
SignalType = Literal["BUY", "SELL", "HOLD"]


# Request Schemas
class EmailSubscribeRequest(BaseModel):
    """Request body for email subscription."""
    email: EmailStr


# Response Schemas
class SignalResponse(BaseModel):
    """Single signal response."""
    id: UUID | str
    symbol: str
    timestamp: datetime
    signal_type: SignalType
    strength: float = Field(..., ge=0, le=100, description="Confidence score 0-100")
    reasoning: List[str]
    price_at_signal: float | None

    @field_serializer('id')
    def serialize_uuid(self, value: UUID | str) -> str:
        """Convert UUID to string for JSON serialization."""
        return str(value)

    class Config:
        from_attributes = True


class SignalListResponse(BaseModel):
    """List of signals response."""
    signals: List[SignalResponse]
    total: int


class MarketDataResponse(BaseModel):
    """Market data response."""
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int

    class Config:
        from_attributes = True


class IndicatorResponse(BaseModel):
    """Indicator data response."""
    symbol: str
    timestamp: datetime
    rsi: float | None
    ema_12: float | None
    ema_26: float | None
    macd: float | None
    macd_signal: float | None
    macd_histogram: float | None

    class Config:
        from_attributes = True


class EmailSubscribeResponse(BaseModel):
    """Email subscription response."""
    message: str
    email: str


class EmailSubscriberSummary(BaseModel):
    """Admin-facing subscriber summary."""
    email: EmailStr
    subscribed_at: datetime | None = None
    confirmed: bool
    confirmed_at: datetime | None = None
    unsubscribed: bool
    confirmation_token: str | None = None
    unsubscribe_token: str | None = None


class EmailSubscriberListResponse(BaseModel):
    """Paginated subscriber list response."""
    subscribers: List[EmailSubscriberSummary]
    total: int


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str
    database: str


class BacktestSummaryResponse(BaseModel):
    """Placeholder backtest summary response."""
    symbol: str
    range: str
    trades: int
    win_rate: float
    avg_return: float
    total_return: float
    last_trained_at: datetime | None = None
    notes: str | None = None
