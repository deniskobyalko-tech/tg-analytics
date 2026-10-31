"""CSV export for channel posts and metrics."""

import csv
import io

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.channel import Channel, ChannelSnapshot
from app.models.post import Post
from app.schemas.common import ApiResponse

router = APIRouter(tags=["export"])


@router.get("/channels/{username}/export")
async def export_channel(
    username: str,
    format: str = "csv",
    type: str = "posts",
    db: AsyncSession = Depends(get_db),
):
    username = username.lstrip("@").lower()
    result = await db.execute(select(Channel).where(Channel.username == username))
    channel = result.scalar_one_or_none()
    if channel is None:
        return ApiResponse(success=False, error="Channel not found")

    output = io.StringIO()
    writer = csv.writer(output)

    if type == "metrics":
        writer.writerow(["date", "subscribers", "avg_views", "er", "posts_count"])
        result = await db.execute(
            select(ChannelSnapshot)
            .where(ChannelSnapshot.channel_id == channel.id)
            .order_by(ChannelSnapshot.date)
        )
        for s in result.scalars():
            writer.writerow([s.date, s.subscribers, s.avg_views, s.er, s.posts_count])
    else:
        writer.writerow(["date", "post_id", "text_preview", "views", "forwards", "reactions", "comments", "is_ad"])
        result = await db.execute(
            select(Post).where(Post.channel_id == channel.id).order_by(Post.date.desc())
        )
        for p in result.scalars():
            preview = (p.text or "")[:100]
            writer.writerow([p.date, p.telegram_post_id, preview, p.views, p.forwards, p.reactions, p.comments_count, p.is_ad])

    output.seek(0)
    filename = f"{username}_{type}.csv"
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
