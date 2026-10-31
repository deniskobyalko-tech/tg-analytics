"""Catalog (directory) and categories endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.category import ChannelCategory
from app.models.channel import Channel
from app.schemas.channel import ChannelOut
from app.schemas.common import ApiResponse, PaginationMeta

router = APIRouter(tags=["catalog"])

ALLOWED_SORT = {"subscribers_count", "avg_views", "er", "posts_per_week"}


@router.get("/categories")
async def get_categories(db: AsyncSession = Depends(get_db)) -> ApiResponse:
    result = await db.execute(select(ChannelCategory).order_by(ChannelCategory.name))
    categories = result.scalars().all()
    return ApiResponse(
        success=True,
        data=[{"id": c.id, "name": c.name, "slug": c.slug} for c in categories],
    )


@router.get("/catalog")
async def get_catalog(
    category: str | None = None,
    min_subscribers: int | None = None,
    status: str | None = None,
    sort: str = "subscribers_count",
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    limit = min(limit, 100)
    query = select(Channel)

    if category:
        query = query.join(ChannelCategory).where(ChannelCategory.slug == category)
    if min_subscribers:
        query = query.where(Channel.subscribers_count >= min_subscribers)
    if status:
        query = query.where(Channel.status == status)

    sort_col = sort if sort in ALLOWED_SORT else "subscribers_count"
    query = query.order_by(getattr(Channel, sort_col).desc())

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * limit
    result = await db.execute(query.offset(offset).limit(limit))
    channels = result.scalars().all()

    return ApiResponse(
        success=True,
        data=[ChannelOut.model_validate(c).model_dump() for c in channels],
        meta=PaginationMeta(total=total, page=page, limit=limit),
    )
