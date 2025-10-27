# Operations Runbook

_Primary audience_: developers and operators running the Signals pipeline in Prefect Cloud.

## 1. Manual Flow Commands

All commands assume you are inside `pipe/` with the virtualenv activated (`source venv/bin/activate`).

| Action | Command |
| --- | --- |
| Backfill two years of history | `python -m flows.historical_backfill --symbols BTC-USD,AAPL --backfill-range 2y` |
| Replay + backtest last two years | `python -m flows.signal_replay --symbols BTC-USD,AAPL --range-label 2y` |
| Generate latest intraday signals | `python -m flows.signal_generation --symbols BTC-USD,AAPL` |
| Send email notifications manually | `python -m flows.notification_sender --min-strength 70` |

> **Tip:** For quick local testing without Prefect Cloud, call `.fn` on any flow (e.g. `signal_replay_flow.fn(symbols=["BTC-USD"])`).

## 2. Register Prefect Deployments

```bash
cd pipe
prefect cloud login                            # once per environment
python -m deployments.register --work-pool default-prefect-managed-wp
```

Deployments created:

- `historical-backfill/manual-backfill` — manual trigger only (use Prefect UI or CLI).
- `signal-generation/intraday-15m` — runs every 15 minutes.
- `signal-replay/replay-daily` — runs daily at 00:15 UTC.
- `notification-sender/notify-strong-signals` — runs 10 minutes after each quarter-hour.

Use a different work pool via `--work-pool my-pool`. Add `--dry-run` to preview without applying.

## 3. Enable / Disable Automation

Pause or resume any deployment via CLI:

```bash
prefect deployment pause signal-generation/intraday-15m
prefect deployment resume signal-generation/intraday-15m
```

Delete the deployment entirely if you no longer want automation:

```bash
prefect deployment delete signal-generation/intraday-15m
```

## 4. Environment Variables & Secrets

Configure the following in Prefect Cloud > Work Pools > Infrastructure Overrides (or in your agent environment):

| Name | Description |
| --- | --- |
| `DATABASE_URL` | Postgres connection string (same as backend). |
| `ALPHA_VANTAGE_API_KEY` | For intraday data. |
| `RESEND_API_KEY` | Resend email API key. |
| `RESEND_FROM_EMAIL` | Verified sender (Resend). |
| `SIGNAL_NOTIFY_THRESHOLD` | Minimum strength before emails are sent. |
| `SIGNAL_SYMBOLS` | Optional comma-separated override for default symbols. |

## 5. Monitoring & Verification

1. **Prefect UI** — check the Flow Runs page for success/failures.
2. **Admin dashboards** — visit `/admin/backtests` and `/admin/subscribers` after runs to confirm data landed.
3. **Database sanity check** — e.g. `SELECT symbol, signal_type, generated_at FROM signals ORDER BY generated_at DESC LIMIT 20;`
4. **Emails** — watch your sandbox inbox while testing `notification-sender`.

## 6. Troubleshooting

- **Alpha Vantage rate limits**: flows log `Alpha Vantage informational response` and fall back to Yahoo automatically. Consider staggering schedules or upgrading the key.
- **Backfill taking too long**: run once manually, then rely on nightly replay/intraday flows.
- **Notifications too chatty**: raise `SIGNAL_NOTIFY_THRESHOLD` or pause the `notify-strong-signals` deployment.

Keep this runbook updated whenever schedules, work pools, or env vars change.
