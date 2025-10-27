"""
Prefect deployment registration helper.

Usage (from the `pipe/` directory):

    python -m deployments.register --work-pool default-prefect-managed-wp

Requires `prefect cloud login` beforehand. Pass `--dry-run` to preview
without creating deployments.
"""

from __future__ import annotations

import argparse
import os
from typing import Optional

from flows.historical_backfill import historical_backfill_flow
from flows.signal_generation import signal_generation_flow
from flows.signal_replay import signal_replay_flow
from flows.notification_sender import notification_sender_flow


def deploy_flow(
    flow,
    name: str,
    work_pool: str,
    *,
    cron: Optional[str] = None,
    description: Optional[str] = None,
    parameters: Optional[dict] = None,
    tags: Optional[list[str]] = None,
    dry_run: bool = False,
) -> None:
    schedule_kwargs = {}
    if cron:
        schedule_kwargs["cron"] = cron
        schedule_kwargs["timezone"] = "UTC"

    if dry_run:
        verb = "Would deploy"
        schedule_desc = f"cron={cron}" if cron else "manual"
        print(f"[dry-run] {verb} {flow.name}/{name} ({schedule_desc}) on work pool '{work_pool}'")
        return

    deployment_id = flow.deploy(
        name,
        work_pool_name=work_pool,
        build=False,
        push=False,
        description=description,
        parameters=parameters,
        tags=tags or [],
        enforce_parameter_schema=False,
        **schedule_kwargs,
    )
    print(f"Registered {flow.name}/{name} (deployment id: {deployment_id})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Register Prefect Cloud deployments for Signals flows.")
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

    deploy_flow(
        historical_backfill_flow,
        name="manual-backfill",
        work_pool=args.work_pool,
        description="Manually trigger multi-year daily backfills.",
        parameters={"backfill_range": "2y"},
        tags=["backfill", "manual"],
        dry_run=args.dry_run,
    )

    deploy_flow(
        signal_generation_flow,
        name="intraday-15m",
        work_pool=args.work_pool,
        description="Fetch intraday bars and store BUY/SELL/HOLD signals.",
        cron="*/15 * * * *",
        tags=["signals", "intraday"],
        dry_run=args.dry_run,
    )

    deploy_flow(
        signal_replay_flow,
        name="replay-daily",
        work_pool=args.work_pool,
        description="Rebuild signals/backtests for the last 2 years every night.",
        cron="15 0 * * *",
        parameters={"range_label": "2y"},
        tags=["signals", "replay"],
        dry_run=args.dry_run,
    )

    deploy_flow(
        notification_sender_flow,
        name="notify-strong-signals",
        work_pool=args.work_pool,
        description="Email subscribers when signal strength crosses the notify threshold.",
        cron="10,25,40,55 * * * *",
        tags=["notifications"],
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
