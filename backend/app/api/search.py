"""Full-text channel search endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.channel import Channel
from app.schemas.channel import ChannelOut
from app.schemas.common import ApiResponse, PaginationMeta

router = APIRouter(tags=["search"])


@router.get("/search")
async def search_channels(
    q: str = "",
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    if not q.strip():
        return ApiResponse(success=True, data=[], meta=PaginationMeta(total=0, page=page, limit=limit))

    limit = min(limit, 100)
    pattern = f"%{q.strip()}%"

    query = select(Channel).where(
        or_(
            Channel.title.ilike(pattern),
            Channel.description.ilike(pattern),
            Channel.username.ilike(pattern),
        )
    )

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * limit
    result = await db.execute(
        query.order_by(Channel.subscribers_count.desc()).offset(offset).limit(limit)
    )
    channels = result.scalars().all()

    return ApiResponse(
        success=True,
        data=[ChannelOut.model_validate(c).model_dump() for c in channels],
        meta=PaginationMeta(total=total, page=page, limit=limit),
    )
