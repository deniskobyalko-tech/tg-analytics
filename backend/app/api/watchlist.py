"""Shared watchlist API: add/remove channels for Tier 2 enrichment."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.channel import Channel
from app.schemas.channel import ChannelOut
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


@router.get("")
async def get_watchlist(db: AsyncSession = Depends(get_db)) -> ApiResponse:
    result = await db.execute(
        select(Channel).where(Channel.is_tracked.is_(True)).order_by(Channel.title)
    )
    channels = result.scalars().all()
    return ApiResponse(
        success=True,
        data=[ChannelOut.model_validate(c).model_dump() for c in channels],
    )


@router.post("/{username}")
async def add_to_watchlist(
    username: str,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    username = username.lstrip("@").lower()
    result = await db.execute(select(Channel).where(Channel.username == username))
    channel = result.scalar_one_or_none()
    if channel is None:
        return ApiResponse(success=False, error="Channel not found. Analyze it first.")
    channel.is_tracked = True
    await db.commit()
    return ApiResponse(success=True, data=ChannelOut.model_validate(channel).model_dump())


@router.delete("/{username}")
async def remove_from_watchlist(
    username: str,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    username = username.lstrip("@").lower()
    result = await db.execute(select(Channel).where(Channel.username == username))
    channel = result.scalar_one_or_none()
    if channel is None:
        return ApiResponse(success=False, error="Channel not found")
    channel.is_tracked = False
    await db.commit()
    return ApiResponse(success=True, data={"removed": username})
