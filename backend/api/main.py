"""
Trading Signals API

FastAPI application for serving trading signals, market data, and email subscriptions.
"""

import logging
import re
from typing import List, Tuple
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, Response, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException
from .config import settings
from .database import get_db
from .routers import signals, market_data, subscribe, backtests

# Configure logging
logger = logging.getLogger(__name__)

# Initialize rate limiter (per IP)
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="Signals API — Market insights made human",
    description=(
        "The Signals API delivers automated trading insights derived from RSI and EMA indicators. "
        "Currently supports AAPL and BTC-USD, with plans to expand into ETFs and forex. "
        "Signals refresh daily at 10 PM UTC, each including both a confidence score (0–100) "
        "and a plain-English summary of the market condition.\n\n"
        "Designed for professionals who value clarity and transparency in data—no hype, no noise."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Register rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

ALLOWED_METHODS = ["GET", "POST", "DELETE", "OPTIONS"]
ALLOWED_HEADERS = [
    "Content-Type",
    "Authorization",
    "Accept",
    "Accept-Language",
    "Content-Language",
]


def _prepare_cors(values: List[str]) -> Tuple[List[str], str | None]:
    """Split exact origins and wildcard rules for CORSMiddleware."""

    exact: List[str] = []
    regexes: List[str] = []

    for origin in values:
        normalized = origin.rstrip("/")
        if "*" in normalized:
            pattern = "^" + re.escape(normalized).replace(r"\*", ".*") + "$"
            regexes.append(pattern)
        elif normalized:
            exact.append(normalized)

    combined_regex = "|".join(regexes) if regexes else None
    return exact, combined_regex


allowed_origins, allowed_regex = _prepare_cors(settings.CORS_ORIGINS)
allowed_origin_set = set(allowed_origins)
allowed_origin_pattern = re.compile(allowed_regex) if allowed_regex else None


def _origin_allowed(origin: str | None) -> bool:
    if not origin:
        return False
    if origin in allowed_origin_set:
        return True
    if allowed_origin_pattern and allowed_origin_pattern.fullmatch(origin):
        return True
    return False


# CORS middleware - allow localhost + Vercel deployments (production-ready security)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=allowed_regex,
    allow_credentials=False,  # API is stateless (no cookies/sessions)
    allow_methods=ALLOWED_METHODS,
    allow_headers=ALLOWED_HEADERS,  # Standard headers browsers may send
)


# Ensure Access-Control headers are always set, even if upstream rewrites strip them.
@app.middleware("http")
async def ensure_cors_headers(request: Request, call_next):
    origin = request.headers.get("origin")

    if request.method == "OPTIONS" and _origin_allowed(origin):
        headers = {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": ", ".join(ALLOWED_METHODS),
            "Access-Control-Allow-Headers": ", ".join(ALLOWED_HEADERS),
            "Access-Control-Max-Age": "86400",
            "Vary": "Origin",
        }
        return Response(status_code=204, headers=headers)

    response = await call_next(request)
    if _origin_allowed(origin):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers.setdefault("Vary", "Origin")
    return response


# Input validation middleware - normalize malicious input errors to 422
@app.middleware("http")
async def validate_malicious_patterns(request: Request, call_next):
    """
    Detect common attack patterns in URLs and return 422 instead of 404/400.

    This middleware improves API consistency by catching malicious inputs
    (path traversal, SQL injection, XSS, null bytes) and returning proper
    validation errors rather than generic 404s.
    """
    path = request.url.path
    query = str(request.url.query)

    # Patterns that indicate malicious input
    # Note: Check both raw and URL-decoded versions
    malicious_patterns = [
        r'\.\.[/\\]',           # Path traversal: ../ or ..\
        r'%2e%2e[/\\]',         # URL-encoded path traversal
        r'<script',              # XSS: <script>
        r'%3cscript',            # URL-encoded <script>
        r'<iframe',              # XSS: <iframe>
        r'%3ciframe',            # URL-encoded <iframe>
        r'javascript:',          # XSS: javascript:
        r'onerror=',            # XSS: onerror attribute
        r'onload=',             # XSS: onload attribute
        r'\x00',                # Null byte
        r'%00',                 # URL-encoded null byte (caught by Vercel, but we log it)
        r'(union|select|drop|insert|delete|update|exec)\s+(from|table|database)',  # SQL injection
        r"('|\")(or|and)\s*('|\")?\s*=\s*('|\")?",  # SQL: ' OR '1'='1
        r'%27(or|and)%27',      # URL-encoded SQL: 'or'
        r';\s*(drop|delete|truncate)',  # SQL: ; DROP TABLE
        r'%3b.*(drop|delete)',  # URL-encoded ; DROP
        r'--\s*$',              # SQL comment
        r'%2d%2d',              # URL-encoded --
        r'/etc/passwd',         # System file access
        r'/proc/self',          # Process info access
        r'\.\.;',               # Path traversal variant
    ]

    # Check path and query for malicious patterns
    full_url = f"{path}?{query}" if query else path

    for pattern in malicious_patterns:
        if re.search(pattern, full_url, re.IGNORECASE):
            logger.warning(
                f"Malicious pattern detected: {pattern} in URL: {full_url[:100]}"
            )
            return JSONResponse(
                status_code=422,
                content={
                    "detail": [
                        {
                            "loc": ["path"],
                            "msg": "Invalid input detected",
                            "type": "value_error.malicious_input"
                        }
                    ]
                }
            )

    try:
        response = await call_next(request)

        # Catch 400 Bad Request from upstream (Vercel/ASGI) for null bytes
        # and convert to 422 for consistency
        if response.status_code == 400:
            # Check if it's likely a malformed request (null bytes, etc.)
            if '%00' in full_url or '\x00' in full_url:
                return JSONResponse(
                    status_code=422,
                    content={
                        "detail": [
                            {
                                "loc": ["path"],
                                "msg": "Invalid character detected (null byte)",
                                "type": "value_error.malicious_input"
                            }
                        ]
                    }
                )
        return response

    except StarletteHTTPException as e:
        # If we get a 404 and the path contains suspicious characters,
        # convert to 422 for consistency
        if e.status_code == 404:
            # Check for URL-encoded suspicious patterns
            suspicious_patterns = ['%3c', '%3e', '%7b', '%7d', '%24', '%5c', '%22', '%27']
            if any(pattern in path.lower() for pattern in suspicious_patterns):
                return JSONResponse(
                    status_code=422,
                    content={
                        "detail": [
                            {
                                "loc": ["path"],
                                "msg": "Invalid path format",
                                "type": "value_error.invalid_path"
                            }
                        ]
                    }
                )
        # For all other errors, let them through
        raise


# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


# Include routers
app.include_router(signals.router, prefix="/api/signals", tags=["signals"])
app.include_router(market_data.router, prefix="/api/market-data", tags=["market-data"])
app.include_router(subscribe.router, prefix="/api/subscribe", tags=["subscribe"])
app.include_router(backtests.router, prefix="/api/backtests", tags=["backtests"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Trading Signals API", "version": "0.1.0"}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Serve favicon from public directory."""
    # Vercel automatically serves files from public/** via CDN
    return RedirectResponse("/favicon.ico", status_code=307)


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Detailed health check including database connection."""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        # Log full error internally
        logger.error(f"Health check failed: {e}", exc_info=True)
        # Return generic error to API (don't leak connection details)
        return {
            "status": "degraded",
            "database": "disconnected",
            "error": "Database connection failed",
        }
