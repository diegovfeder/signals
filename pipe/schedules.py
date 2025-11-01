"""
Prefect Flow Schedules (Single-Flow MVP)
"""

from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule
from flows.signal_generation import signal_generation_flow


def deploy_signal_flow():
    """Deploy single signal_generation flow daily (deprecated - use deployments/register.py instead)."""
    deployment = Deployment.build_from_flow(
        flow=signal_generation_flow,
        name="signal-generation-daily",
        schedule=CronSchedule(cron="0 22 * * *"),  # 10 PM UTC daily
        work_queue_name="default",
    )
    deployment.apply()
    print("✓ Deployed: signal_generation (daily at 10 PM UTC)")


if __name__ == "__main__":
    deploy_signal_flow()
