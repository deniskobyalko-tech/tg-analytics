"""Compare 2-4 channels side by side. Auto-analyzes missing channels."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.channel import Channel
from app.schemas.channel import ChannelOut
from app.schemas.common import ApiResponse
from app.services.scraper import fetch_channel_preview, fetch_channel_posts
from app.services.analyzer import calculate_er, detect_ad_post
from app.services.categorizer import categorize_channel
from app.models.post import Post
from app.models.category import ChannelCategory
from datetime import datetime, timezone

router = APIRouter(tags=["compare"])


async def _auto_analyze(username: str, db: AsyncSession) -> Channel | None:
    """Quick-analyze a channel that's not yet in DB."""
    try:
        preview = await fetch_channel_preview(username)
        raw_posts = await fetch_channel_posts(username)
    except Exception:
        return None

    if not preview.get("title"):
        return None

    views = [p.get("views", 0) for p in raw_posts if p.get("views", 0) > 0]
    avg_views = int(sum(views) / len(views)) if views else 0
    subscribers = preview.get("subscribers_count", 0)
    er = calculate_er(avg_views, subscribers)
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    placeholder_tid = -(abs(hash(username)) % (10 ** 15))
    channel = Channel(
        telegram_id=placeholder_tid,
        username=username,
        title=preview.get("title") or username,
        description=preview.get("description"),
        avatar_url=preview.get("avatar_url"),
        subscribers_count=subscribers,
        avg_views=avg_views,
        er=er,
        posts_per_week=0.0,
        last_scraped_at=now,
    )
    db.add(channel)
    await db.flush()

    # Auto-categorize
    cat_slug = categorize_channel(channel.title, channel.description)
    cat_result = await db.execute(
        select(ChannelCategory).where(ChannelCategory.slug == cat_slug)
    )
    cat = cat_result.scalar_one_or_none()
    if cat:
        channel.category_id = cat.id

    # Save posts
    for raw in raw_posts:
        post_id = raw.get("telegram_post_id", 0)
        if not post_id:
            continue
        raw_date = raw.get("date")
        try:
            if isinstance(raw_date, str):
                post_date = datetime.fromisoformat(raw_date).replace(tzinfo=None)
            elif isinstance(raw_date, datetime):
                post_date = raw_date.replace(tzinfo=None)
            else:
                post_date = now
        except (ValueError, TypeError):
            post_date = now
        db.add(Post(
            channel_id=channel.id,
            telegram_post_id=post_id,
            text=raw.get("text"),
            date=post_date,
            views=raw.get("views", 0),
            forwards=raw.get("forwards", 0),
            reactions=raw.get("reactions", 0),
            is_ad=detect_ad_post(raw.get("text") or ""),
            fwd_from_channel=raw.get("fwd_from_channel"),
        ))

    await db.commit()
    await db.refresh(channel)
    return channel


@router.get("/compare")
async def compare_channels(
    channels: str = "",
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    usernames = [u.strip().lower().lstrip("@") for u in channels.split(",") if u.strip()]

    if len(usernames) < 2 or len(usernames) > 4:
        return ApiResponse(success=False, error="Укажите 2-4 канала для сравнения")

    result = await db.execute(
        select(Channel).where(Channel.username.in_(usernames))
    )
    found = {c.username: c for c in result.scalars().all()}

    # Auto-analyze missing channels
    errors = []
    for u in usernames:
        if u not in found:
            channel = await _auto_analyze(u, db)
            if channel:
                found[u] = channel
            else:
                errors.append(u)

    if errors:
        return ApiResponse(
            success=False,
            error=f"Каналы не найдены или приватные: {', '.join(errors)}",
        )

    # Return in the order requested
    data = [ChannelOut.model_validate(found[u]).model_dump() for u in usernames]
    return ApiResponse(success=True, data=data)
