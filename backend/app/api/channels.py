from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.channel import Channel, ChannelSnapshot
from app.models.post import Post
from app.schemas.channel import ChannelAnalyzeRequest, ChannelOut, ChannelSnapshotOut
from app.schemas.common import ApiResponse, PaginationMeta
from app.schemas.post import PostOut
from app.services.analyzer import calculate_er, detect_ad_post
from app.services.scraper import fetch_channel_posts, fetch_channel_preview

router = APIRouter(prefix="/channels", tags=["channels"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _compute_posts_per_week(posts: list[dict]) -> float:
    """Return average posts per week from a list of raw post dicts."""
    if not posts:
        return 0.0
    dates: list[datetime] = []
    for p in posts:
        raw = p.get("date")
        if not raw:
            continue
        try:
            dt = datetime.fromisoformat(raw) if isinstance(raw, str) else raw
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=UTC)
            dates.append(dt)
        except (ValueError, TypeError):
            continue
    if len(dates) < 2:
        return float(len(dates))
    span_days = (max(dates) - min(dates)).total_seconds() / 86_400
    if span_days < 1:
        return float(len(dates))
    return round(len(dates) / (span_days / 7), 2)


async def _enrich_with_telethon(channel_id: int) -> None:
    """Background task: Tier-2 Telethon enrichment (only for tracked channels)."""
    # Import lazily to avoid errors when Telethon is not configured.
    try:
        from app.services.telethon_client import fetch_channel_data  # noqa: F401
        # Real enrichment logic would go here. Placeholder for now.
    except Exception:
        pass


# ---------------------------------------------------------------------------
# POST /api/channels/analyze
# ---------------------------------------------------------------------------

@router.post("/analyze", response_model=ApiResponse)
async def analyze_channel(
    body: ChannelAnalyzeRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """Tier-1 (sync): scrape t.me/s/, persist, return immediately.
    Tier-2 (async background): optionally enrich via Telethon for tracked channels.
    """
    username = body.username  # already cleaned by validator

    # 1. Scrape channel preview and posts (Tier 1)
    try:
        preview = await fetch_channel_preview(username)
        raw_posts = await fetch_channel_posts(username)
    except Exception as exc:
        return ApiResponse(success=False, error=f"Failed to fetch channel data: {exc}")

    if not preview.get("title"):
        return ApiResponse(success=False, error=f"Channel '@{username}' not found or private")

    # 2. Compute metrics from scraped data
    views_list = [p.get("views", 0) for p in raw_posts if p.get("views", 0) > 0]
    avg_views = int(sum(views_list) / len(views_list)) if views_list else 0
    subscribers = preview.get("subscribers_count", 0)
    er = calculate_er(avg_views, subscribers)
    posts_per_week = _compute_posts_per_week(raw_posts)

    # 3. Upsert Channel row
    result = await db.execute(select(Channel).where(Channel.username == username))
    channel = result.scalar_one_or_none()

    now = datetime.now(timezone.utc).replace(tzinfo=None)

    if channel is None:
        # telegram_id is unknown from scraper; use a negative hash as placeholder
        # so the UNIQUE constraint is satisfied. Telethon enrichment will update it.
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
            posts_per_week=posts_per_week,
            last_scraped_at=now,
        )
        db.add(channel)
        await db.flush()  # get channel.id
    else:
        channel.title = preview.get("title") or channel.title
        channel.description = preview.get("description") or channel.description
        channel.avatar_url = preview.get("avatar_url") or channel.avatar_url
        channel.subscribers_count = subscribers
        channel.avg_views = avg_views
        channel.er = er
        channel.posts_per_week = posts_per_week
        channel.last_scraped_at = now

    # 4. Upsert Posts
    for raw in raw_posts:
        post_id = raw.get("telegram_post_id", 0)
        if not post_id:
            continue
        res = await db.execute(
            select(Post).where(
                Post.channel_id == channel.id,
                Post.telegram_post_id == post_id,
            )
        )
        post = res.scalar_one_or_none()
        raw_date = raw.get("date")
        try:
            post_date = datetime.fromisoformat(raw_date) if isinstance(raw_date, str) else (raw_date or now)
        except (ValueError, TypeError):
            post_date = now

        if post is None:
            post = Post(
                channel_id=channel.id,
                telegram_post_id=post_id,
                text=raw.get("text"),
                date=post_date,
                views=raw.get("views", 0),
                forwards=raw.get("forwards", 0),
                reactions=raw.get("reactions", 0),
                is_ad=detect_ad_post(raw.get("text") or ""),
                fwd_from_channel=raw.get("fwd_from_channel"),
            )
            db.add(post)
        else:
            post.views = raw.get("views", post.views)
            post.forwards = raw.get("forwards", post.forwards)
            post.reactions = raw.get("reactions", post.reactions)

    await db.commit()
    await db.refresh(channel)

    # 5. Schedule Tier-2 Telethon enrichment for tracked channels
    if channel.is_tracked and settings.TELETHON_ENABLED:
        background_tasks.add_task(_enrich_with_telethon, channel.id)

    out = ChannelOut(
        id=channel.id,
        telegram_id=channel.telegram_id,
        username=channel.username,
        title=channel.title,
        description=channel.description,
        avatar_url=channel.avatar_url,
        category=None,
        subscribers_count=channel.subscribers_count,
        avg_views=channel.avg_views,
        er=channel.er,
        posts_per_week=channel.posts_per_week,
        last_scraped_at=channel.last_scraped_at,
    )
    return ApiResponse(success=True, data=out.model_dump())


# ---------------------------------------------------------------------------
# GET /api/channels/{username}
# ---------------------------------------------------------------------------

@router.get("/{username}", response_model=ApiResponse)
async def get_channel(
    username: str,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    username = username.lstrip("@").lower()
    result = await db.execute(select(Channel).where(Channel.username == username))
    channel = result.scalar_one_or_none()
    if channel is None:
        return ApiResponse(success=False, error=f"Channel '{username}' not found")
    out = ChannelOut(
        id=channel.id,
        telegram_id=channel.telegram_id,
        username=channel.username,
        title=channel.title,
        description=channel.description,
        avatar_url=channel.avatar_url,
        category=None,
        subscribers_count=channel.subscribers_count,
        avg_views=channel.avg_views,
        er=channel.er,
        posts_per_week=channel.posts_per_week,
        last_scraped_at=channel.last_scraped_at,
    )
    return ApiResponse(success=True, data=out.model_dump())


# ---------------------------------------------------------------------------
# GET /api/channels/{username}/history
# ---------------------------------------------------------------------------

@router.get("/{username}/history", response_model=ApiResponse)
async def get_channel_history(
    username: str,
    days: int = 30,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    username = username.lstrip("@").lower()
    result = await db.execute(select(Channel).where(Channel.username == username))
    channel = result.scalar_one_or_none()
    if channel is None:
        return ApiResponse(success=False, error=f"Channel '{username}' not found")

    since = datetime.now(timezone.utc).replace(tzinfo=None).date() - timedelta(days=days)
    snaps_result = await db.execute(
        select(ChannelSnapshot)
        .where(ChannelSnapshot.channel_id == channel.id, ChannelSnapshot.date >= since)
        .order_by(ChannelSnapshot.date)
    )
    snapshots = snaps_result.scalars().all()
    data = [
        ChannelSnapshotOut(
            date=datetime.combine(s.date, datetime.min.time()).replace(tzinfo=UTC),
            subscribers=s.subscribers,
            avg_views=s.avg_views,
            er=s.er,
            posts_count=s.posts_count,
        ).model_dump()
        for s in snapshots
    ]
    return ApiResponse(success=True, data=data)


# ---------------------------------------------------------------------------
# GET /api/channels/{username}/posts
# ---------------------------------------------------------------------------

@router.get("/{username}/posts", response_model=ApiResponse)
async def get_channel_posts(
    username: str,
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    username = username.lstrip("@").lower()
    result = await db.execute(select(Channel).where(Channel.username == username))
    channel = result.scalar_one_or_none()
    if channel is None:
        return ApiResponse(success=False, error=f"Channel '{username}' not found")

    # Total count using func.count (not len())
    count_result = await db.execute(
        select(func.count()).select_from(Post).where(Post.channel_id == channel.id)
    )
    total = count_result.scalar_one()

    offset = (page - 1) * limit
    posts_result = await db.execute(
        select(Post)
        .where(Post.channel_id == channel.id)
        .order_by(Post.date.desc())
        .offset(offset)
        .limit(limit)
    )
    posts = posts_result.scalars().all()
    data = [PostOut.model_validate(p).model_dump() for p in posts]
    meta = PaginationMeta(total=total, page=page, limit=limit)
    return ApiResponse(success=True, data=data, meta=meta)
