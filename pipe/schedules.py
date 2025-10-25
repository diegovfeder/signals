"""
Prefect Flow Schedules (Single-Flow MVP)
"""

from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule
from flows.signal_generation import signal_generation_flow


def deploy_signal_flow():
    """Deploy single signal_generation flow on 15-minute cron."""
    deployment = Deployment.build_from_flow(
        flow=signal_generation_flow,
        name="signal-generation-15min",
        schedule=CronSchedule(cron="0,15,30,45 * * * *"),
        work_queue_name="default",
    )
    deployment.apply()
    print("✓ Deployed: signal_generation (every 15 minutes)")


if __name__ == "__main__":
    deploy_signal_flow()
