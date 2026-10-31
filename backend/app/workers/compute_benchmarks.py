"""Periodic worker: compute category benchmarks (daily averages)."""

import logging
from datetime import date

from sqlalchemy import select

from app.core.database import async_session
from app.models.benchmark import CategoryBenchmark
from app.models.category import ChannelCategory
from app.models.channel import Channel

logger = logging.getLogger(__name__)


def calculate_category_averages(channels: list[dict]) -> dict:
    """Calculate average metrics from a list of channel dicts."""
    n = len(channels)
    if n == 0:
        return {
            "avg_subscribers": 0, "avg_er": 0.0,
            "avg_views": 0, "avg_posts_per_week": 0.0,
            "channel_count": 0,
        }
    return {
        "avg_subscribers": round(sum(c["subscribers_count"] for c in channels) / n),
        "avg_er": round(sum(c["er"] for c in channels) / n, 2),
        "avg_views": round(sum(c["avg_views"] for c in channels) / n),
        "avg_posts_per_week": round(sum(c["posts_per_week"] for c in channels) / n, 2),
        "channel_count": n,
    }


async def compute_all_benchmarks() -> None:
    """Compute and store benchmarks for each category."""
    today = date.today()

    async with async_session() as db:
        cats = (await db.execute(select(ChannelCategory))).scalars().all()

        for cat in cats:
            result = await db.execute(
                select(Channel).where(Channel.category_id == cat.id)
            )
            channels = result.scalars().all()

            data = [
                {
                    "subscribers_count": c.subscribers_count,
                    "er": c.er,
                    "avg_views": c.avg_views,
                    "posts_per_week": c.posts_per_week,
                }
                for c in channels
            ]
            avgs = calculate_category_averages(data)

            # Upsert benchmark for today
            existing = await db.execute(
                select(CategoryBenchmark).where(
                    CategoryBenchmark.category_id == cat.id,
                    CategoryBenchmark.date == today,
                )
            )
            benchmark = existing.scalar_one_or_none()
            if benchmark is None:
                benchmark = CategoryBenchmark(
                    category_id=cat.id,
                    date=today,
                    **avgs,
                )
                db.add(benchmark)
            else:
                for key, val in avgs.items():
                    setattr(benchmark, key, val)

        await db.commit()
        logger.info("Computed benchmarks for %d categories", len(cats))
