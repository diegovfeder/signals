"""
Prefect Flow Schedules

Deploy and schedule all flows to Prefect Cloud.
"""

from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule
from flows.market_data_ingestion import market_data_ingestion_flow
from flows.indicator_calculation import indicator_calculation_flow
from flows.signal_generation import signal_generation_flow
from flows.notification_sender import notification_sender_flow


def deploy_all_flows():
    """Deploy all flows with hourly schedules."""

    # Market Data Ingestion - Every hour at :05
    market_data_deployment = Deployment.build_from_flow(
        flow=market_data_ingestion_flow,
        name="market-data-ingestion-hourly",
        schedule=CronSchedule(cron="5 * * * *"),
        work_queue_name="default"
    )
    market_data_deployment.apply()
    print("✓ Deployed: market_data_ingestion (hourly at :05)")

    # Indicator Calculation - Every hour at :10
    indicator_deployment = Deployment.build_from_flow(
        flow=indicator_calculation_flow,
        name="indicator-calculation-hourly",
        schedule=CronSchedule(cron="10 * * * *"),
        work_queue_name="default"
    )
    indicator_deployment.apply()
    print("✓ Deployed: indicator_calculation (hourly at :10)")

    # Signal Generation - Every hour at :15
    signal_deployment = Deployment.build_from_flow(
        flow=signal_generation_flow,
        name="signal-generation-hourly",
        schedule=CronSchedule(cron="15 * * * *"),
        work_queue_name="default"
    )
    signal_deployment.apply()
    print("✓ Deployed: signal_generation (hourly at :15)")

    # Notification Sender - Every hour at :20
    notification_deployment = Deployment.build_from_flow(
        flow=notification_sender_flow,
        name="notification-sender-hourly",
        schedule=CronSchedule(cron="20 * * * *"),
        work_queue_name="default"
    )
    notification_deployment.apply()
    print("✓ Deployed: notification_sender (hourly at :20)")

    print("\n✓ All flows deployed successfully!")


if __name__ == "__main__":
    deploy_all_flows()
