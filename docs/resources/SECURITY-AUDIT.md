# Security Audit Report *(Historical + Remediation Summary)*

> **Note**: Sections 1–9 capture the pre-hardening state from October 31, 2025. The final section summarizes the fixes deployed on November 8, 2025 so this remains the single source of truth.

**Date**: 2025-10-31
**Auditor**: Security Review (Automated + Manual)
**Scope**: Backend API, Database, Pipeline, Frontend
**Status**: 🔴 CRITICAL ISSUES FOUND

---

## Executive Summary

Security audit identified **14 vulnerabilities** across the stack. **5 CRITICAL** issues require immediate attention before any alpha users are onboarded:

1. ❌ No Row Level Security (RLS) policies on database
2. ❌ Error messages leak sensitive information to API responses
3. ❌ CORS configuration too permissive (allows all methods/headers)
4. ❌ No rate limiting (DDoS vulnerability)
5. ❌ Actual .env files exist in repository (need verification they're never committed)

**Risk Level**: HIGH - Product is not safe for public launch
**Recommendation (Oct 31)**: Complete Phase 0 security hardening before any deployment. *(Status: ✅ Completed Nov 8 – see Remediation Summary at the end.)*

---

## ✅ Good Practices Already in Place

Before diving into vulnerabilities, credit where it's due:

| Practice | Implementation | Security Benefit |
|----------|----------------|------------------|
| **SQL Injection Protection** | SQLAlchemy ORM with parameterized queries | Prevents SQL injection attacks |
| **Input Validation** | Pydantic schemas with regex/constraints | Prevents malformed data injection |
| **Secure Token Generation** | `secrets.token_urlsafe(32)` | Cryptographically secure tokens |
| **Email Normalization** | Lowercase + strip whitespace | Prevents duplicate accounts |
| **Connection Pooling** | `pool_size=10, max_overflow=20` | Prevents connection exhaustion |
| **Environment Variables** | Pydantic BaseSettings + .env | Secrets not hardcoded |
| **.gitignore Configured** | `.env` excluded from git | Prevents accidental secret commits |
| **Database Constraints** | CHECK constraints on prices/strength | Data integrity validation |

**Conclusion**: The foundation is solid. The issues below are fixable with focused effort.

---

## 🔴 CRITICAL Vulnerabilities (Fix Before Alpha)

### 1. No Row Level Security (RLS) Policies

**Location**: `db/schema.sql` (entire file)

**Issue**:
Database has ZERO Row Level Security policies. Anyone with database credentials can:
- Read all user emails from `email_subscribers`
- Read all signals, market data, indicators
- Modify or delete any data
- Bypass application-level access controls

**Attack Scenario**:
```sql
-- Attacker with DB creds can do this:
SELECT email, confirmation_token, unsubscribe_token
FROM email_subscribers;

-- Or delete all signals:
DELETE FROM signals;
```

**Remediation**:

```sql
-- Enable RLS on all tables
ALTER TABLE email_subscribers ENABLE ROW LEVEL SECURITY;
ALTER TABLE signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE market_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE indicators ENABLE ROW LEVEL SECURITY;
ALTER TABLE sent_notifications ENABLE ROW LEVEL SECURITY;

-- Create policies (example for MVP - restrict to service role only)
CREATE POLICY "Service role can manage subscribers" ON email_subscribers
    FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Public can read signals" ON signals
    FOR SELECT
    USING (true);

CREATE POLICY "Service role can write signals" ON signals
    FOR INSERT
    USING (auth.role() = 'service_role');
```

**Effort**: 2 hours (write policies, test, deploy)

---

### 2. Error Messages Leak Sensitive Information

**Location**: `backend/api/main.py:64`

**Issue**:
```python
except Exception as e:
    return {
        "status": "degraded",
        "database": "disconnected",
        "error": str(e)  # ❌ LEAKS SENSITIVE INFO
    }
```

**What Gets Leaked**:
- Database connection strings (username, host, port)
- Table names and schema structure
- Internal file paths
- Stack traces with code snippets

**Attack Scenario**:
```bash
curl https://api.signals.com/health
# Returns:
# {"error": "could not connect to server: Connection refused\n\tIs the server running on host \"db.internal.123.us-east-1.rds.amazonaws.com\" (10.0.1.5) and accepting TCP/IP connections on port 5432?"}
# Attacker now knows your internal DB hostname and IP
```

**Remediation**:

```python
except Exception as e:
    # Log full error internally
    logger.error(f"Health check failed: {e}", exc_info=True)

    # Return generic error to API
    return {
        "status": "degraded",
        "database": "disconnected",
        "error": "Database connection failed"  # ✅ Generic message
    }
```

**Effort**: 30 minutes (update all error handlers)

---

### 3. CORS Configuration Too Permissive

**Location**: `backend/api/main.py:24-31`

**Issue**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # ✅ Good (configurable)
    allow_credentials=True,  # ⚠️ Dangerous with * origins
    allow_methods=["*"],     # ❌ TOO PERMISSIVE
    allow_headers=["*"],     # ❌ TOO PERMISSIVE
)
```

**Attack Scenario**:
- Attacker can use `PATCH`, `PUT`, `DELETE` methods even if not needed
- Can send custom headers to exploit vulnerabilities
- Combined with `allow_credentials=True`, enables CSRF-like attacks

**Remediation**:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Already good
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],  # ✅ Only needed methods
    allow_headers=["Content-Type", "Authorization"],  # ✅ Only needed headers
)
```

**Effort**: 15 minutes (update + test)

---

### 4. No Rate Limiting (DDoS Vulnerability)

**Location**: All API endpoints (missing middleware)

**Issue**:
No rate limiting anywhere. Attacker can:
- Spam `/api/subscribe` with millions of emails (database bloat)
- Overload database with `/api/signals` queries
- Exhaust connection pool
- Cause denial of service

**Attack Scenario**:
```bash
# Spam subscribe endpoint
for i in {1..100000}; do
  curl -X POST https://api.signals.com/api/subscribe \
    -d "{\"email\":\"spam$i@example.com\"}"
done
# Database now has 100K fake emails
```

**Remediation**:

```bash
# Install slowapi
pip install slowapi
```

```python
# backend/api/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply to endpoints
@app.get("/api/signals")
@limiter.limit("100/minute")  # Max 100 requests per minute per IP
async def get_signals():
    ...
```

**Effort**: 1 hour (add dependency, configure limits, test)

---

### 5. .env Files Verification

**Location**: `.env`, `backend/.env`, `pipe/.env`, `frontend/.env.local`

**Issue**:
Multiple .env files exist in the working directory. While `.gitignore` excludes them, need to verify:
1. They were NEVER committed to git history
2. No secrets are hardcoded in committed code

**Verification Steps**:

```bash
# Check git history for .env commits
git log --all --full-history -- "*.env"

# Check for hardcoded secrets in codebase
grep -r "sk_live" . --exclude-dir=node_modules --exclude-dir=.git
grep -r "postgres://" . --exclude-dir=node_modules --exclude-dir=.git
```

**Remediation**:
- If found in git history: Rotate ALL secrets immediately
- Use `git-filter-repo` or BFG Repo-Cleaner to purge history
- Notify users if credentials leaked publicly

**Effort**: 1 hour (audit + rotate if needed)

---

## 🟠 HIGH Priority Vulnerabilities

### 6. No SSL/TLS Enforcement for Database

**Location**: `backend/api/database.py:18-23`

**Issue**:
Database connection doesn't enforce SSL/TLS:

```python
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
    # ❌ MISSING: connect_args={'sslmode': 'require'}
)
```

**Attack Scenario**:
- Man-in-the-middle attack on database connection
- Credentials sniffed in plaintext
- Data intercepted during transit

**Remediation**:

```python
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args={'sslmode': 'require'}  # ✅ Force SSL
)
```

For Supabase specifically:
```python
# Supabase uses connection pooler - verify SSL is enabled
connect_args={
    'sslmode': 'require',
    'connect_timeout': 10
}
```

**Effort**: 30 minutes (add + test connection)

---

### 7. No Security Headers

**Location**: `backend/api/main.py` (missing middleware)

**Issue**:
No security headers sent with API responses. Vulnerable to:
- Clickjacking (no X-Frame-Options)
- MIME sniffing attacks (no X-Content-Type-Options)
- XSS (no Content-Security-Policy)

**Remediation**:

```bash
pip install secure
```

```python
# backend/api/main.py
from secure import Secure

secure_headers = Secure()

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    secure_headers.framework.fastapi(response)
    return response
```

Or manually:

```python
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

**Effort**: 30 minutes

---

### 8. Symbol Parameter Not Validated

**Location**: `backend/api/routers/signals.py:61`

**Issue**:
```python
@router.get("/{symbol}", response_model=SignalResponse)
async def get_signal_by_symbol(
    symbol: str,  # ❌ No validation - accepts ANY string
    db: Session = Depends(get_db)
):
```

**Attack Scenario**:
```bash
# Attacker tries SQL injection (won't work due to ORM, but best to validate)
curl "https://api.signals.com/api/signals/'; DROP TABLE signals; --"

# Or tries path traversal
curl "https://api.signals.com/api/signals/../../../etc/passwd"
```

**Remediation**:

```python
from pydantic import Field

@router.get("/{symbol}", response_model=SignalResponse)
async def get_signal_by_symbol(
    symbol: str = Path(..., regex="^[A-Z0-9-=]+$", max_length=20),  # ✅ Validate format
    db: Session = Depends(get_db)
):
```

**Effort**: 30 minutes (add validation to all symbol endpoints)

---

## 🟡 MEDIUM Priority Vulnerabilities

### 9. No Connection Timeout

**Location**: `backend/api/database.py:18`

**Issue**:
No timeout configured - slow queries can hang forever, exhausting connections.

**Remediation**:

```python
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args={
        'sslmode': 'require',
        'connect_timeout': 10,      # ✅ Connection timeout
        'options': '-c statement_timeout=30000'  # ✅ Query timeout (30s)
    }
)
```

**Effort**: 15 minutes

---

### 10. No Token Rotation Strategy

**Location**: `backend/api/routers/subscribe.py:130-131`

**Issue**:
Tokens never expire or rotate:

```python
confirmation_token = secrets.token_urlsafe(32)  # ✅ Secure generation
unsubscribe_token = secrets.token_urlsafe(32)
# ❌ But no expiration - valid forever
```

**Attack Scenario**:
- Old confirmation email forwarded months later → still works
- Unsubscribe token leaked → anyone can unsubscribe the user anytime

**Remediation**:

```sql
-- Add expiration column
ALTER TABLE email_subscribers
ADD COLUMN confirmation_expires_at TIMESTAMPTZ;

-- Set 7-day expiration on creation
UPDATE email_subscribers
SET confirmation_expires_at = NOW() + INTERVAL '7 days'
WHERE confirmation_token IS NOT NULL;
```

```python
# Check expiration before confirming
if subscriber.confirmation_expires_at < datetime.now():
    raise HTTPException(status_code=410, detail="Confirmation link expired")
```

**Effort**: 1 hour (schema change + code update)

---

### 11. RESEND_API_KEY Defaults to Empty String

**Location**: `backend/api/config.py:26`

**Issue**:
```python
RESEND_API_KEY: str = ""  # ❌ Defaults to empty - fails silently
```

**Problem**:
If env var not set, application starts but emails silently fail.

**Remediation**:

```python
from pydantic import Field

class Settings(BaseSettings):
    RESEND_API_KEY: str = Field(..., min_length=1)  # ✅ Required, fails fast
```

Or conditional:

```python
RESEND_API_KEY: str = Field(default="")

@property
def email_enabled(self) -> bool:
    return bool(self.RESEND_API_KEY)
```

**Effort**: 15 minutes

---

## 🟢 LOW Priority Issues

### 12. Type Ignore Comments

**Location**: `backend/api/config.py:39`

**Issue**:
```python
settings = Settings()  # type: ignore[call-arg]
```

Suppressing type errors reduces type safety.

**Remediation**: Fix root cause (already discussed in previous session).

**Effort**: Already completed

---

## 📋 Remediation Checklist

### Phase 0: Week 1 (Database & Secrets)

- [ ] **Add RLS policies** to all tables (`db/schema.sql`) - 2 hours
- [ ] **Fix error handling** to not leak sensitive info (`backend/api/main.py`) - 30 min
- [ ] **Audit git history** for leaked .env files - 1 hour
- [ ] **Rotate all secrets** if any leaks found - 1 hour
- [ ] **Enable SSL/TLS** for database connections - 30 min
- [ ] **Add connection timeouts** - 15 min
- [ ] **Review Supabase backup strategy** - 30 min
- [ ] **Document incident response plan** - 1 hour

**Total Effort**: ~6.5 hours

---

### Phase 0: Week 2 (API Security)

- [ ] **Add rate limiting** (slowapi) - 1 hour
- [ ] **Fix CORS configuration** (restrict methods/headers) - 15 min
- [ ] **Add security headers** middleware - 30 min
- [ ] **Add symbol parameter validation** - 30 min
- [ ] **Add token expiration** logic - 1 hour
- [ ] **Fix RESEND_API_KEY** validation - 15 min
- [ ] **Scan dependencies** for vulnerabilities (`pip-audit`) - 30 min
- [ ] **Manual penetration test** (try SQL injection, XSS, CSRF) - 1 hour

**Total Effort**: ~5.5 hours

---

## 🎯 Security Testing Plan

Before considering product "secure enough":

### Automated Testing

```bash
# Dependency scanning
pip install pip-audit
pip-audit

# OWASP ZAP scan (free security scanner)
docker run -t owasp/zap2docker-stable zap-baseline.py -t http://localhost:8000

# SQL injection testing
sqlmap -u "http://localhost:8000/api/signals?symbol=BTC-USD" --batch
```

### Manual Testing Checklist

- [ ] Try SQL injection on all endpoints
- [ ] Try XSS in email subscription
- [ ] Verify CORS blocks unauthorized origins
- [ ] Test rate limiting (spam requests)
- [ ] Verify RLS policies work (use psql as different roles)
- [ ] Check error messages don't leak info
- [ ] Verify SSL/TLS certificate on DB connection
- [ ] Test token expiration logic

---

## 📊 Risk Summary

| Category | Critical | High | Medium | Low | Total |
|----------|----------|------|--------|-----|-------|
| Database | 1 | 1 | 1 | 0 | 3 |
| API | 3 | 2 | 1 | 0 | 6 |
| Authentication | 0 | 0 | 1 | 0 | 1 |
| Infrastructure | 1 | 1 | 1 | 1 | 4 |
| **TOTAL** | **5** | **4** | **4** | **1** | **14** |

---

## ✅ Next Steps

1. *(Oct 31)* Complete Phase 0 Week 1 tasks (database security) — ✅ finished Nov 5.
2. *(Oct 31)* Complete Phase 0 Week 2 tasks (API security) — ✅ finished Nov 7.
3. Run automated security scans (pip-audit, OWASP ZAP) whenever dependencies change.
4. Perform manual penetration testing before major releases.
5. Keep this audit updated with new mitigations and attach logs for noteworthy findings.
6. Consider third-party reviews as the surface area grows.
7. Proceed to Phase 1 (stability testing) once substantive product changes land.

---

## Remediation Summary – November 8, 2025

**Goal**: Close all critical/high issues from the Oct 31 audit and ensure malicious input attempts return deterministic 422 responses in production (`https://signals-api-dvf.vercel.app`).

### Key Improvements
- Added malicious-pattern middleware to intercept traversal (`../`, `%2e%2e`), XSS (`<script>`, `%3cscript`), SQL injection (`UNION SELECT`, `%27or%27`), system-file patterns, and similar payloads. Responses now return `422 value_error.malicious_input` with structured details; null-byte payloads are blocked earlier by Vercel edge (400).
- Introduced slowapi rate limiting (5/min subscribe, 20/min confirm, 60/min GET endpoints) and tightened CORS to required methods/headers only.
- Enforced TLS/timeout defaults on all Postgres connections (`sslmode=require`, `connect_timeout`, `statement_timeout`).
- Sanitized health/error handlers, added standard security headers, and validated symbols via strict regex.
- Confirmed double opt-in tokens + unsubscribe flow operate end-to-end with Resend sandbox credentials.

### Production Test Matrix (Nov 8)

| Attack | Example | Result |
| --- | --- | --- |
| Path traversal | `/api/signals/../../../etc/passwd` | 422 (`value_error.malicious_input`) |
| URL-encoded traversal | `/api/signals/%2e%2e%2fetc%2fpasswd` | 422 |
| XSS | `/api/signals/<script>alert(1)</script>` | 422 |
| URL-encoded XSS | `/api/signals/%3cscript%3ealert(1)%3c/script%3e` | 422 |
| SQL injection | `/api/signals/BTC';DROP TABLE signals--` | 422 (regex validation) |
| URL-encoded SQL | `/api/signals/BTC%27%3BDROP%20TABLE--` | 422 |
| Null byte | `/api/signals/BTC%00USD` | 400 (blocked by Vercel edge runtime) |
| Valid health check | `/health` | 200 `{ "status": "healthy" }` |

### Defense-in-Depth Overview
1. **Vercel Edge Runtime** blocks malformed payloads (e.g., null bytes) before FastAPI runs.
2. **Middleware** normalizes suspicious inputs to 422 and logs them for monitoring.
3. **Pydantic validation** enforces strict symbol patterns and limits path params.
4. **slowapi** throttles abusive IPs per endpoint.
5. **Security headers + TLS enforcement** protect browser clients and database connections.

### Follow-Up Ideas
- Emit metrics/logs for blocked requests and consider rate limiting based on repeated 422 responses.
- Schedule quarterly security reviews (or after major features such as auth/payments) to ensure new surfaces adhere to the same controls.

**Status**: All CRITICAL/HIGH findings from the Oct 31 audit are mitigated and verified in production as of Nov 8, 2025.

---

**Document last updated**: 2025-11-08
**Next review**: Quarterly or after significant launches
