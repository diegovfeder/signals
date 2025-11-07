# Testing Email Verification Flow

**Sprint 2 Deliverable** - Email verification, rate limiting, and security hardening.

This guide walks through testing the complete double opt-in email flow locally.

## Prerequisites

1. **Backend running** with environment variables configured:
   ```bash
   cd backend
   # Ensure .env has:
   # - DATABASE_URL (PostgreSQL connection)
   # - RESEND_API_KEY (from https://resend.com/api-keys)
   # - APP_BASE_URL=http://localhost:3000
   # - RESEND_FROM_EMAIL=onboarding@resend.dev

   uv run uvicorn api.main:app --reload --port 8000
   ```

2. **Frontend running**:
   ```bash
   cd frontend
   # Ensure .env.local has:
   # - NEXT_PUBLIC_API_URL=http://localhost:8000

   npm run dev
   # Runs on http://localhost:3000
   ```

3. **Database running** (Docker):
   ```bash
   # From project root
   docker-compose up -d
   ```

4. **Resend account** configured:
   - Sign up at https://resend.com
   - Get API key from https://resend.com/api-keys
   - Set `RESEND_API_KEY` in `backend/.env`

## Testing Flow

### 1. Subscribe to Signals

**Frontend flow**:
1. Navigate to http://localhost:3000
2. Enter email in subscription form
3. Click "Subscribe"
4. Should see: "Subscription pending confirmation. Please check your email."

**Backend logs** (check terminal):
```
[email] Confirmation email sent to user@example.com (ID: abc123xyz)
```

**API endpoint** (alternative to frontend):
```bash
curl -X POST http://localhost:8000/api/subscribe/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

**Expected response**:
```json
{
  "message": "Subscription pending confirmation. Please check your email.",
  "email": "user@example.com"
}
```

**Database verification**:
```sql
SELECT email, confirmed, confirmation_token, subscribed_at
FROM email_subscribers
WHERE email = 'user@example.com';
```

Should show:
- `confirmed = false`
- `confirmation_token` (32-character token)
- `subscribed_at` (timestamp)

---

### 2. Check Email in Resend Dashboard

Since we're using `onboarding@resend.dev` without a custom domain, emails are not delivered but logged in Resend dashboard.

1. Go to https://resend.com/emails
2. Find the confirmation email sent to your test address
3. Copy the confirmation URL from the email body
4. Format: `http://localhost:3000/confirm/{token}`

**Example**:
```
http://localhost:3000/confirm/abc123xyz-token-here
```

---

### 3. Confirm Email Address

**Option A: Click link in email** (if using a real email address with custom domain)

**Option B: Visit confirmation URL directly** (for testing with onboarding@resend.dev):
1. Copy the confirmation URL from Resend dashboard
2. Paste into browser: `http://localhost:3000/confirm/{token}`
3. Should see confirmation page with:
   - ✅ Success checkmark
   - "Email Confirmed!"
   - "You'll now receive trading signals."
   - Auto-redirect to dashboard after 3 seconds

**Backend logs**:
```
INFO:     127.0.0.1:xxxxx - "GET /api/subscribe/confirm/{token} HTTP/1.1" 200 OK
```

**Database verification**:
```sql
SELECT email, confirmed, confirmed_at
FROM email_subscribers
WHERE email = 'user@example.com';
```

Should show:
- `confirmed = true`
- `confirmed_at` (timestamp)

**API endpoint** (direct test):
```bash
TOKEN="your-confirmation-token-here"
curl http://localhost:8000/api/subscribe/confirm/$TOKEN
```

Expected response:
```json
{
  "message": "Email confirmed! You'll now receive trading signals.",
  "email": "user@example.com"
}
```

---

### 4. Test Reactivation Flow

Test what happens when an unsubscribed user re-subscribes:

**Step 1: Unsubscribe first**:
```sql
UPDATE email_subscribers
SET unsubscribed = true
WHERE email = 'user@example.com';
```

**Step 2: Re-subscribe** (via frontend or API):
```bash
curl -X POST http://localhost:8000/api/subscribe/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

**Expected response**:
```json
{
  "message": "Subscription reactivated. Please check your email for confirmation.",
  "email": "user@example.com"
}
```

**Backend logs**:
```
[email] Reactivation email sent to user@example.com (ID: xyz789abc)
```

**Email template**: Should see "Welcome back to Signals!" instead of "Welcome to Signals!"

**Step 3: Confirm reactivation** using new token from Resend dashboard.

**Database verification**:
```sql
SELECT email, confirmed, unsubscribed, confirmation_token
FROM email_subscribers
WHERE email = 'user@example.com';
```

Should show:
- `unsubscribed = false`
- `confirmed = false` (needs re-confirmation)
- `confirmation_token` (new token, different from original)

---

### 5. Test Error Cases

#### Invalid Token
```bash
curl http://localhost:8000/api/subscribe/confirm/invalid-token-123
```

**Expected**: 404 error
```json
{
  "detail": "Invalid or already used confirmation token"
}
```

#### Already Confirmed Token
Try to use the same token twice:

```bash
TOKEN="your-confirmed-token"
curl http://localhost:8000/api/subscribe/confirm/$TOKEN
# First time: 200 OK
curl http://localhost:8000/api/subscribe/confirm/$TOKEN
# Second time: 404 error (already used)
```

#### Duplicate Subscription
Subscribe with same email twice:

```bash
curl -X POST http://localhost:8000/api/subscribe/ \
  -H "Content-Type: application/json" \
  -d '{"email": "confirmed@example.com"}'
```

**Expected**: 409 Conflict
```json
{
  "detail": "Email already subscribed"
}
```

#### Invalid Email Format
```bash
curl -X POST http://localhost:8000/api/subscribe/ \
  -H "Content-Type: application/json" \
  -d '{"email": "not-an-email"}'
```

**Expected**: 422 Validation error (caught by Pydantic `EmailStr`)

---

### 6. Test Rate Limiting

Rate limits (per IP address):
- Subscribe: **5 requests/minute** (1 every 12 seconds)
- Confirm: **20 requests/minute** (1 every 3 seconds)
- Signal reads: **60 requests/minute** (1 per second)

**Test subscribe rate limit**:
```bash
for i in {1..6}; do
  echo "Request $i"
  curl -X POST http://localhost:8000/api/subscribe/ \
    -H "Content-Type: application/json" \
    -d "{\"email\": \"test$i@example.com\"}"
  echo ""
done
```

**Expected**: First 5 succeed, 6th returns:
```json
{
  "error": "Rate limit exceeded: 5 per 1 minute"
}
```

**Test confirm rate limit**:
```bash
for i in {1..21}; do
  curl -s -o /dev/null -w "Request $i: %{http_code}\n" \
    http://localhost:8000/api/subscribe/confirm/fake-token-$i
done
```

**Expected**: First 20 return 404 (invalid token), 21st returns 429 (rate limited)

---

### 7. Test Security Headers

Verify security headers are applied:

```bash
curl -I http://localhost:8000/api/signals/
```

**Expected headers**:
```
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Referrer-Policy: strict-origin-when-cross-origin
```

---

### 8. Test CORS Configuration

Verify CORS is properly restricted:

**Allowed origins**: `http://localhost:3000`, `https://*.vercel.app`
**Allowed methods**: `GET`, `POST`, `DELETE` (NOT `PUT`, `PATCH`)
**Allowed headers**: `Content-Type`, `Authorization` (NOT `*`)

```bash
# Should succeed (localhost:3000)
curl -X OPTIONS http://localhost:8000/api/signals/ \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET"

# Should fail (disallowed origin)
curl -X OPTIONS http://localhost:8000/api/signals/ \
  -H "Origin: http://malicious-site.com" \
  -H "Access-Control-Request-Method: GET"

# Should fail (disallowed method)
curl -X OPTIONS http://localhost:8000/api/signals/ \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: PUT"
```

---

### 9. Test Symbol Validation

Verify path parameters are validated (prevents path traversal):

```bash
# Valid symbol
curl http://localhost:8000/api/signals/BTC-USD
# Expected: 200 OK or 404 (no signals found)

# Invalid symbol (path traversal attempt)
curl http://localhost:8000/api/signals/../../../etc/passwd
# Expected: 422 Validation error

# Invalid symbol (special characters)
curl http://localhost:8000/api/signals/BTC\$USD
# Expected: 422 Validation error
```

**Valid symbols**: `^[A-Z0-9-=]+$` (uppercase letters, numbers, hyphens, equals only)

---

## Quick Verification Checklist

After implementing Sprint 2, verify:

- [ ] Subscribe endpoint sends confirmation email
- [ ] Confirmation page loads at `/confirm/{token}`
- [ ] Confirming token sets `confirmed = true` in database
- [ ] Resubscribing after unsubscribe sends reactivation email
- [ ] Rate limiting blocks excessive requests (5/min subscribe, 60/min reads)
- [ ] Security headers present on all responses
- [ ] CORS restricted to allowed origins/methods/headers
- [ ] Symbol validation blocks invalid characters
- [ ] Health check endpoint doesn't leak DB connection details

---

## Troubleshooting

### Email not sent

**Symptom**: No log entry like `[email] Confirmation email sent to...`

**Checks**:
1. `RESEND_API_KEY` set in `backend/.env`?
   ```bash
   grep RESEND_API_KEY backend/.env
   ```
2. API key valid? Test with Resend CLI:
   ```bash
   curl -X POST https://api.resend.com/emails \
     -H "Authorization: Bearer $RESEND_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"from": "onboarding@resend.dev", "to": "test@example.com", "subject": "Test", "html": "<p>Test</p>"}'
   ```

### Confirmation link invalid

**Symptom**: 404 error when clicking confirmation link

**Checks**:
1. Token expired? (Optional feature not implemented in MVP - tokens never expire)
2. Token already used? Check database:
   ```sql
   SELECT confirmed FROM email_subscribers WHERE confirmation_token = 'your-token';
   ```
   If `confirmed = true`, token was already used.
3. Token format correct? Should be 32-character URL-safe string (e.g., `a1b2c3d4...`)

### Rate limiting not working

**Symptom**: Can send unlimited requests without 429 errors

**Checks**:
1. `slowapi` installed?
   ```bash
   cd backend && uv pip list | grep slowapi
   ```
2. Limiter registered in `main.py`?
   ```bash
   grep "app.state.limiter" backend/api/main.py
   ```
3. Testing from same IP? Rate limiting is per-IP. If using different IPs (proxy/VPN), each IP gets separate limits.

### CORS errors in browser

**Symptom**: Browser shows `CORS policy: No 'Access-Control-Allow-Origin' header`

**Checks**:
1. Frontend origin in `CORS_ORIGINS`?
   ```bash
   grep CORS_ORIGINS backend/.env
   # Should include: ["http://localhost:3000"]
   ```
2. Backend running on correct port?
   ```bash
   # Backend should be on :8000, frontend on :3000
   curl http://localhost:8000/health
   ```
3. Browser dev tools → Network → Check preflight OPTIONS request

### Database connection failed

**Symptom**: Health check shows `"database": "disconnected"`

**Checks**:
1. Docker container running?
   ```bash
   docker ps | grep postgres
   ```
2. Database URL correct in `.env`?
   ```bash
   grep DATABASE_URL backend/.env
   # Should be: postgresql+psycopg://signals_user:signals_password@localhost:5432/trading_signals
   ```
3. Schema loaded?
   ```bash
   docker exec -it signals-postgres psql -U signals_user -d trading_signals -c "\dt"
   # Should show tables: symbols, market_data, indicators, signals, email_subscribers, sent_notifications
   ```

---

## Production Testing (Vercel)

After deploying to Vercel:

1. **Set environment variables** in Vercel dashboard:
   - `DATABASE_URL` (Supabase connection string)
   - `RESEND_API_KEY` (your Resend API key)
   - `APP_BASE_URL` (https://your-frontend.vercel.app)
   - `RESEND_FROM_EMAIL` (onboarding@resend.dev or custom domain)
   - `CORS_ORIGINS` (["https://your-frontend.vercel.app"])

2. **Test subscribe flow**:
   ```bash
   curl -X POST https://your-backend.vercel.app/api/subscribe/ \
     -H "Content-Type: application/json" \
     -d '{"email": "your-real-email@example.com"}'
   ```

3. **Check Resend dashboard** for sent email

4. **Click confirmation link** in email (should redirect to `https://your-frontend.vercel.app/confirm/{token}`)

5. **Verify in Supabase**:
   - Go to Supabase Dashboard → Table Editor → `email_subscribers`
   - Find your email, check `confirmed = true`

---

## Next Steps

After verifying the email flow works:

1. **Deploy to production** (see `docs/DEPLOYMENT.md`)
2. **Configure custom domain** in Resend (optional, for branded emails)
3. **Add email open/click tracking** (optional, Phase 3)
4. **Implement token expiration** (optional, Phase 3)
5. **Write automated tests** (pytest for backend, see `pipe/tests/README.md`)

---

## Related Documentation

- **Backend API**: `/Users/diegovfeder/workspace/jobs/signals/backend/api/routers/subscribe.py`
- **Email module**: `/Users/diegovfeder/workspace/jobs/signals/backend/api/email.py`
- **Confirmation page**: `/Users/diegovfeder/workspace/jobs/signals/frontend/src/app/confirm/[token]/page.tsx`
- **Architecture**: `/Users/diegovfeder/workspace/jobs/signals/docs/ARCHITECTURE.md`
- **Sprint 2 tasks**: `/Users/diegovfeder/workspace/jobs/signals/docs/TODOs.md` (Sprint 2)
