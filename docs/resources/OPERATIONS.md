# Operations Guide

> **Last Updated**: 2025-11-06
> **Applies to**: Production MVP (Yahoo-only daily flows)

_Primary audience_: developers and operators running the Signals pipeline in Prefect Cloud.

**Related**: [MVP](../MVP.md) | [Architecture](../ARCHITECTURE.md) | [Technical Analysis](TECHNICAL-ANALYSIS.md)

---

## 1. Manual Flow Commands

All commands run from the project root using `uv` (so env vars in `.env` files are respected):

| Action | Command |
| --- | --- |
| Backfill historical data (new symbols) | `uv run --directory pipe python -m pipe.flows.market_data_backfill --symbols AAPL,BTC-USD --backfill-range 10y` |
| Sync latest daily bars | `uv run --directory pipe python -m pipe.flows.market_data_sync --symbols AAPL,BTC-USD` |
| Recompute indicators + signals | `uv run --directory pipe python -m pipe.flows.signal_analyzer --symbols AAPL,BTC-USD` |
| Dispatch notifications | `uv run --directory pipe python -m pipe.flows.notification_dispatcher --min-strength 60` |

> **Tip:** For quick local testing, run flows directly: `cd pipe && uv run python -m flows.market_data_backfill --symbols BTC-USD --backfill-range 1m`

---

## 2. Register Prefect Deployments

```bash
prefect cloud login  # once per environment
uv run --directory pipe python -m deployments.register --work-pool default-prefect-managed-wp
```

> **Tip:** The deploy helper automatically loads `pipe/.env`. Keep your Supabase pooler string (`SUPABASE_URL_SESSION_POOLER`) there so deployments always override `DATABASE_URL` without touching your local dev settings.

**Deployments created:**

| Flow | Deployment Name | Schedule | Description |
| --- | --- | --- | --- |
| `market-data-backfill` | `manual-backfill` | Manual only | Load multi-year history for new symbols |
| `market-data-sync` | `daily-sync` | 10:00 PM UTC | Fetch latest daily OHLCV bars |
| `signal-analyzer` | `daily-analyzer` | 10:15 PM UTC | Generate BUY/SELL/HOLD signals |
| `notification-dispatcher` | `daily-notifier` | 10:30 PM UTC | Email subscribers about strong signals |

**Schedule Cadence**: All automated flows run daily (10:00 PM, 10:15 PM, 10:30 PM UTC) to ensure data flows properly (sync → analyze → notify).

Use `--dry-run` to preview deployments without creating them:
```bash
uv run python -m deployments.register --dry-run
```

---

## 3. Enable / Disable Automation

Pause or resume any deployment via CLI:

```bash
prefect deployment pause market-data-sync/daily-sync
prefect deployment resume market-data-sync/daily-sync
```

Delete a deployment entirely:

```bash
prefect deployment delete market-data-sync/daily-sync
```

---

## 4. Environment Variables & Secrets

Configure the following in Prefect Cloud → Work Pools → Infrastructure Overrides (or in your agent environment):

| Name | Description | Required |
| --- | --- | --- |
| `DATABASE_URL` | Postgres connection string (same as backend) | ✅ Yes |
| `SUPABASE_URL_SESSION_POOLER` | Supabase pooled connection string. Store this in `pipe/.env`; the deploy helper injects it as `DATABASE_URL` for Prefect deployments. | ✅ Yes (production) |
| `RESEND_API_KEY` | Resend email API key | ✅ Yes |
| `RESEND_FROM_EMAIL` | Verified sender email (Resend) | ✅ Yes |
| `SIGNAL_NOTIFY_THRESHOLD` | Minimum strength before emails are sent (default: 60) | No |
| `SIGNAL_SYMBOLS` | Comma-separated symbol override (default: AAPL,BTC-USD) | No |

---

## 5. Monitoring & Verification

### Check Flow Success

1. **Prefect UI** → Flow Runs page for success/failures
2. **Database queries**:
   ```sql
   -- Check latest market data
   SELECT symbol, COUNT(*), MAX(timestamp)
   FROM market_data
   GROUP BY symbol;

   -- Check latest signals
   SELECT symbol, signal_type, strength, timestamp
   FROM signals
   ORDER BY timestamp DESC
   LIMIT 10;
   ```
3. **Admin dashboard** → `/admin/subscribers` to verify email confirmations / unsubscribes
4. **Resend dashboard** → Confirm deliverability + bounce metrics when notification dispatcher runs

### Expected Daily Flow Sequence

```
10:00 PM UTC → market_data_sync runs
              ↓ (stores daily OHLCV bars)
10:15 PM UTC → signal_analyzer runs
              ↓ (generates signals from DB)
10:30 PM UTC → notification_dispatcher runs
              ↓ (emails strong signals)
```

---

## 6. Troubleshooting

### Common Issues

**Problem**: Backfill taking too long
**Solution**: Run the 10y backfill once per new symbol; nightly sync keeps data fresh. For partial reruns, reduce `--backfill-range` or pass `--backfill-days`.

**Problem**: No signals generated
**Solution**:
- Check that `market_data_sync` ran successfully first
- Verify indicators were calculated: `SELECT COUNT(*) FROM indicators WHERE symbol = 'BTC-USD';`
- Check signal strength threshold (may be too high)

**Problem**: Too many email notifications
**Solution**:
- Raise `SIGNAL_NOTIFY_THRESHOLD` (e.g., from 60 to 70)
- Or pause the `daily-notifier` deployment temporarily

**Problem**: Yahoo Finance data fetch fails
**Solution**:
- Ensure symbol format (`BTC-USD`, `AAPL`)
- Verify provider rate limits; rerun with `--symbols SYMBOL --backfill-range 1y` to reduce payload
- Inspect Prefect run logs; if repeated failures occur, see Task Seeds → Provider fallback

**Problem**: Database connection errors
**Solution**:
- Verify `DATABASE_URL` format: `postgresql://user:pass@host:port/dbname`
- Check database is accessible from deployment environment
- Test connection: `psql $DATABASE_URL -c "SELECT 1;"`

---

## 7. Maintenance

> **⚠️ Update this doc when**: Adding new flows, changing schedules, updating deployment configs, or modifying environment variables.

**Regular tasks:**
- Review Prefect Flow Runs weekly for failures
- Check email delivery rates in Resend dashboard
- Monitor database size and consider archiving old data (future)
- Update `SIGNAL_SYMBOLS` when adding new assets

---

Keep this guide updated to reflect operational changes.
