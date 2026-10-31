from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.core.config import settings
from app.workers.compute_benchmarks import compute_all_benchmarks
from app.workers.compute_overlaps import compute_all_overlaps
from app.workers.compute_similarities import compute_all_similarities
from app.workers.detect_anomalies import detect_all_anomalies
from app.workers.update_channels import update_all_channels

scheduler = AsyncIOScheduler()


def start_scheduler():
    scheduler.add_job(
        update_all_channels,
        "interval",
        hours=settings.SCRAPE_INTERVAL_HOURS,
        id="update_channels",
        replace_existing=True,
    )
    scheduler.add_job(
        compute_all_similarities,
        "interval",
        hours=12,
        id="compute_similarities",
        replace_existing=True,
    )
    scheduler.add_job(
        compute_all_overlaps,
        "interval",
        hours=12,
        id="compute_overlaps",
        replace_existing=True,
    )
    scheduler.add_job(
        compute_all_benchmarks,
        "interval",
        hours=24,
        id="compute_benchmarks",
        replace_existing=True,
    )
    scheduler.add_job(
        detect_all_anomalies,
        "interval",
        hours=6,
        id="detect_anomalies",
        replace_existing=True,
    )
    scheduler.start()
