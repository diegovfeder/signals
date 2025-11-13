"""
Prefect deployment registration helper.

Usage (from the project root directory):

    python -m pipe.deployments.register --work-pool default-prefect-managed-wp

Requires `prefect cloud login` beforehand. Pass `--dry-run` to preview
without creating deployments.
"""

from __future__ import annotations

import argparse
import os
from collections.abc import Sequence
from pathlib import Path
from typing import Any, cast

from prefect.client.schemas.schedules import CronSchedule
from dotenv import load_dotenv

PIPE_DIR = Path(__file__).resolve().parent.parent

# Load pipeline-specific .env automatically so operators don't have to export manually.
# We intentionally do NOT load a repo-root .env because that file is absent in prod.
load_dotenv(PIPE_DIR / ".env")

try:
    from flows.market_data_backfill import market_data_backfill_flow
    from flows.market_data_sync import market_data_sync_flow
    from flows.signal_analyzer import signal_analyzer_flow
    from flows.notification_dispatcher import notification_dispatcher_flow
except ImportError:
    from pipe.flows.market_data_backfill import market_data_backfill_flow
    from pipe.flows.market_data_sync import market_data_sync_flow
    from pipe.flows.signal_analyzer import signal_analyzer_flow
    from pipe.flows.notification_dispatcher import notification_dispatcher_flow
from prefect_github.repository import GitHubRepository


GITHUB_BLOCK_NAME = "gh-prefect-signals"
_CACHED_REPOSITORY: GitHubRepository | None = None
SUGGESTED_ENV_VARS: tuple[str, ...] = (
    "DATABASE_URL",
    "RESEND_API_KEY",
    "SIGNAL_SYMBOLS",
    "LLM_PROVIDER",
    "DEEPSEEK_API_KEY",
    "POSTHOG_PROJECT_API_KEY",
    "POSTHOG_HOST",
)

# Allow operators to provide production credentials without mutating their local dev env.
# If one of these override env vars is set, we prefer it when populating Prefect job envs.
ENVIRONMENT_OVERRIDES: dict[str, Sequence[str]] = {
    "DATABASE_URL": ("SUPABASE_URL_SESSION_POOLER",),
}


def _collect_job_env() -> dict[str, str]:
    env: dict[str, str] = {}
    missing: list[str] = []
    for key in SUGGESTED_ENV_VARS:
        value: str | None = None
        source: str | None = None
        for override in ENVIRONMENT_OVERRIDES.get(
            key, ()
        ):  # Prefer explicit override vars
            override_value = os.getenv(override)
            if override_value:
                value = override_value
                source = override
                break

        if value is None:
            value = os.getenv(key)
            if value:
                source = key

        if key == "DATABASE_URL" and value and "://" not in value:
            print(
                "[env] Skipping DATABASE_URL from local shell because it doesn't look like a connection string."
            )
            value = None
            source = None

        if value:
            env[key] = value
            if source:
                print(f"[env] Using {source} for {key} in Prefect job environment.")
        else:
            missing.append(key)
    if missing:
        print(
            "[env] Missing environment variables locally (not exported): "
            + ", ".join(missing)
        )
    return env


DEFAULT_PIP_PACKAGES = [
    "prefect>=2.19.0",
    "prefect-github>=0.3.1",
    "requests>=2.31.0",
    "polars>=1.0.0",
    "numpy>=1.26.2",
    "sqlalchemy>=2.0.35",
    "psycopg[binary,pool]>=3.1.0",
    "resend>=2.19.0",
    "posthog>=3.0.0",
    "httpx>=0.28.1",
    "python-dotenv==1.0.0",
]

JOB_VARIABLES: dict[str, Any] = {"pip_packages": DEFAULT_PIP_PACKAGES}
_job_env = _collect_job_env()
if _job_env:
    JOB_VARIABLES["env"] = _job_env


def get_repository() -> GitHubRepository:
    global _CACHED_REPOSITORY
    if _CACHED_REPOSITORY is None:
        repo = GitHubRepository.load(GITHUB_BLOCK_NAME)
        _CACHED_REPOSITORY = cast(GitHubRepository, repo)
    assert _CACHED_REPOSITORY is not None
    return _CACHED_REPOSITORY


def deploy_flow(
    flow,
    entrypoint: str,
    name: str,
    work_pool: str,
    *,
    cron: str | None = None,
    description: str | None = None,
    parameters: dict[str, Any] | None = None,
    tags: list[str] | None = None,
    dry_run: bool = False,
) -> None:
    schedule_kwargs = {}
    if cron:
        schedule_kwargs["schedule"] = CronSchedule(cron=cron, timezone="UTC")

    if dry_run:
        verb = "Would deploy"
        schedule_desc = f"cron={cron}" if cron else "manual"
        print(
            f"[dry-run] {verb} {flow.name}/{name} ({schedule_desc}) on work pool '{work_pool}'"
        )
        return

    repository = get_repository()
    remote_flow = flow.from_source(source=repository, entrypoint=entrypoint)

    deployment_id = remote_flow.deploy(
        name,
        work_pool_name=work_pool,
        build=False,
        push=False,
        job_variables=JOB_VARIABLES,
        description=description,
        parameters=parameters,
        tags=tags or [],
        enforce_parameter_schema=False,
        **schedule_kwargs,
    )
    print(f"Registered {flow.name}/{name} (deployment id: {deployment_id})")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Register Prefect Cloud deployments for Signals flows."
    )
    parser.add_argument(
        "--work-pool",
        default=os.getenv("PREFECT_WORK_POOL", "default-prefect-managed-wp"),
        help="Prefect work pool name to attach deployments to (default: %(default)s).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview deployments without creating them.",
    )
    args = parser.parse_args()

    # Manual backfill for onboarding new symbols
    deploy_flow(
        market_data_backfill_flow,
        entrypoint="pipe/flows/market_data_backfill.py:market_data_backfill_flow",
        name="manual-backfill",
        work_pool=args.work_pool,
        description="Manual trigger to load multi-year history for new symbols.",
        parameters={"backfill_range": "10y"},
        tags=["backfill", "manual", "onboarding"],
        dry_run=args.dry_run,
    )

    # Daily market data sync at 10 PM UTC
    deploy_flow(
        market_data_sync_flow,
        entrypoint="pipe/flows/market_data_sync.py:market_data_sync_flow",
        name="daily-sync",
        work_pool=args.work_pool,
        description="Fetch the latest daily OHLCV bar for all symbols (10 PM UTC).",
        cron="0 22 * * *",  # 10 PM UTC
        tags=["market-data", "daily", "scheduled"],
        dry_run=args.dry_run,
    )

    # Signal analysis at 10:15 PM UTC (15 min after market data sync)
    deploy_flow(
        signal_analyzer_flow,
        entrypoint="pipe/flows/signal_analyzer.py:signal_analyzer_flow",
        name="daily-analyzer",
        work_pool=args.work_pool,
        description="Analyze daily data and generate BUY/SELL/HOLD signals (10:15 PM UTC).",
        cron="15 22 * * *",  # 10:15 PM UTC
        tags=["signals", "daily", "scheduled"],
        dry_run=args.dry_run,
    )

    # Notification dispatcher at 10:30 PM UTC (15 min after signal analysis)
    deploy_flow(
        notification_dispatcher_flow,
        entrypoint="pipe/flows/notification_dispatcher.py:notification_dispatcher_flow",
        name="daily-notifier",
        work_pool=args.work_pool,
        description="Email subscribers about strong signals (10:30 PM UTC).",
        cron="30 22 * * *",  # 10:30 PM UTC
        parameters={"min_strength": 60, "window_minutes": 1440},
        tags=["notifications", "daily", "scheduled"],
        dry_run=args.dry_run,
    )

    print("\n✅ All deployments registered successfully!")
    print("\nSchedule summary:")
    print("  - 10:00 PM UTC: market-data-sync (fetch latest daily bars)")
    print("  - 10:15 PM UTC: signal-analyzer (generate signals)")
    print("  - 10:30 PM UTC: notification-dispatcher (send emails)")


if __name__ == "__main__":
    main()
