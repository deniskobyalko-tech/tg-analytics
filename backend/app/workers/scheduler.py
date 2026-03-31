from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.core.config import settings
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
    scheduler.start()
