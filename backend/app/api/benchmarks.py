"""Category benchmarks API."""

from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.benchmark import CategoryBenchmark
from app.models.category import ChannelCategory
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/benchmarks", tags=["benchmarks"])


@router.get("/{category_slug}")
async def get_benchmarks(
    category_slug: str,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    result = await db.execute(
        select(ChannelCategory).where(ChannelCategory.slug == category_slug)
    )
    cat = result.scalar_one_or_none()
    if cat is None:
        return ApiResponse(success=False, error=f"Category '{category_slug}' not found")

    # Current (latest)
    latest = await db.execute(
        select(CategoryBenchmark)
        .where(CategoryBenchmark.category_id == cat.id)
        .order_by(CategoryBenchmark.date.desc())
        .limit(1)
    )
    current = latest.scalar_one_or_none()

    # 30-day trend
    since = date.today() - timedelta(days=30)
    trend_result = await db.execute(
        select(CategoryBenchmark)
        .where(
            CategoryBenchmark.category_id == cat.id,
            CategoryBenchmark.date >= since,
        )
        .order_by(CategoryBenchmark.date)
    )
    trend = trend_result.scalars().all()

    return ApiResponse(
        success=True,
        data={
            "category": {"id": cat.id, "name": cat.name, "slug": cat.slug},
            "current": {
                "avg_subscribers": current.avg_subscribers if current else 0,
                "avg_er": current.avg_er if current else 0,
                "avg_views": current.avg_views if current else 0,
                "avg_posts_per_week": current.avg_posts_per_week if current else 0,
                "channel_count": current.channel_count if current else 0,
                "date": str(current.date) if current else None,
            },
            "trend": [
                {
                    "date": str(b.date),
                    "avg_subscribers": b.avg_subscribers,
                    "avg_er": b.avg_er,
                    "avg_views": b.avg_views,
                }
                for b in trend
            ],
        },
    )
