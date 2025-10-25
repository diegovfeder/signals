"""
SQLAlchemy ORM Models

Database models corresponding to the schema.
"""

from sqlalchemy import Column, String, DECIMAL, BigInteger, TIMESTAMP, Boolean, ARRAY, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from .database import Base
import uuid


class Symbol(Base):
    """Tracked assets (BTC-USD, ETH-USD, TSLA)."""
    __tablename__ = "symbols"

    symbol = Column(String(20), primary_key=True)
    name = Column(String(100), nullable=False)
    asset_type = Column(String(20), nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class MarketData(Base):
    """Raw OHLCV market data."""
    __tablename__ = "market_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(20), ForeignKey("symbols.symbol", ondelete="CASCADE"))
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)
    open = Column(DECIMAL(20, 8), nullable=False)
    high = Column(DECIMAL(20, 8), nullable=False)
    low = Column(DECIMAL(20, 8), nullable=False)
    close = Column(DECIMAL(20, 8), nullable=False)
    volume = Column(BigInteger, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class Indicator(Base):
    """Calculated technical indicators."""
    __tablename__ = "indicators"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(20), ForeignKey("symbols.symbol", ondelete="CASCADE"))
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)

    # RSI
    rsi = Column(DECIMAL(5, 2))

    # EMA
    ema_12 = Column(DECIMAL(20, 8))
    ema_26 = Column(DECIMAL(20, 8))

    # MACD (optional)
    macd = Column(DECIMAL(10, 4))
    macd_signal = Column(DECIMAL(10, 4))
    macd_histogram = Column(DECIMAL(10, 4))

    calculated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class Signal(Base):
    """Generated trading signals."""
    __tablename__ = "signals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(20), ForeignKey("symbols.symbol", ondelete="CASCADE"))
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)
    signal_type = Column(String(10), nullable=False)
    strength = Column(DECIMAL(5, 2), nullable=False)
    reasoning = Column(ARRAY(Text), nullable=False)
    price_at_signal = Column(DECIMAL(20, 8))
    idempotency_key = Column(String(255), unique=True)
    rule_version = Column(String(50))
    generated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class EmailSubscriber(Base):
    """Email subscribers with double opt-in."""
    __tablename__ = "email_subscribers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    subscribed_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    confirmed = Column(Boolean, default=False)
    confirmation_token = Column(String(64), unique=True)
    confirmed_at = Column(TIMESTAMP(timezone=True))
    last_email_sent_at = Column(TIMESTAMP(timezone=True))
    unsubscribed = Column(Boolean, default=False)
    unsubscribe_token = Column(String(64), unique=True)


class SentNotification(Base):
    """Audit log of sent email notifications."""
    __tablename__ = "sent_notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False)
    signal_id = Column(UUID(as_uuid=True), ForeignKey("signals.id", ondelete="CASCADE"))
    sent_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
