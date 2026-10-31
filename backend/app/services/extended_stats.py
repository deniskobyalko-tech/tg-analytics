"""Orchestrator: combines Bot API + Telethon data for extended stats."""

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.admin_log import ChannelAdminLog
from app.models.channel import Channel
from app.models.invite_link import ChannelInviteLink
from app.models.member import ChannelMember
from app.models.post import Post
from app.services.bot_client import check_bot_is_admin, get_bot

logger = logging.getLogger(__name__)

CACHE_TTL = timedelta(hours=1)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def is_cache_fresh(fetched_at: datetime | None) -> bool:
    if fetched_at is None:
        return False
    return (_utcnow() - fetched_at) < CACHE_TTL


async def fetch_extended_stats(channel: Channel, db: AsyncSession) -> dict:
    """Main entry point: fetch extended stats, using cache if fresh."""

    # Check cache
    if is_cache_fresh(channel.extended_fetched_at):
        return await _build_response_from_db(channel, db)

    # Check bot configured
    bot = get_bot()
    if bot is None or not settings.BOT_TOKEN:
        return {"bot_connected": False, "bot_username": "", "instructions": "BOT_TOKEN not configured"}

    # Check bot is admin
    is_admin, chat_id = await check_bot_is_admin(username=channel.username)
    if not is_admin:
        bot_me = await bot.get_me()
        return {
            "bot_connected": False,
            "bot_username": bot_me.username,
            "instructions": f"Добавьте @{bot_me.username} в админы канала для расширенной статистики",
        }

    # Fetch fresh data from Telethon
    telethon_available = True
    try:
        await _fetch_and_store_telethon(channel, db)
    except Exception as e:
        logger.error("Telethon fetch failed for %s: %s", channel.username, e)
        telethon_available = False

    # Update cache timestamp
    channel.bot_is_admin = True
    channel.extended_fetched_at = _utcnow()
    await db.commit()

    response = await _build_response_from_db(channel, db)
    response["telethon_available"] = telethon_available
    return response


async def _fetch_and_store_telethon(channel: Channel, db: AsyncSession) -> None:
    """Fetch data from Telethon and save to DB."""
    from app.services.telethon_client import (
        fetch_admin_log,
        fetch_invite_links,
        fetch_participants,
    )

    # Admin log
    events = await fetch_admin_log(channel.username)
    await db.execute(delete(ChannelAdminLog).where(ChannelAdminLog.channel_id == channel.id))
    for ev in events:
        db.add(ChannelAdminLog(channel_id=channel.id, **ev))

    await asyncio.sleep(1)

    # Participants
    members = await fetch_participants(channel.username)
    await db.execute(delete(ChannelMember).where(ChannelMember.channel_id == channel.id))
    for m in members:
        db.add(ChannelMember(channel_id=channel.id, **m))

    await asyncio.sleep(1)

    # Invite links
    links = await fetch_invite_links(channel.username)
    await db.execute(delete(ChannelInviteLink).where(ChannelInviteLink.channel_id == channel.id))
    for lnk in links:
        db.add(ChannelInviteLink(channel_id=channel.id, **lnk))

    await db.flush()


async def _build_response_from_db(channel: Channel, db: AsyncSession) -> dict:
    """Build extended stats response from DB data."""

    # Comments (replies)
    posts = (await db.execute(
        select(Post)
        .where(Post.channel_id == channel.id)
        .order_by(Post.replies_count.desc())
        .limit(100)
    )).scalars().all()

    total_replies = sum(p.replies_count for p in posts)
    avg_replies = round(total_replies / len(posts), 1) if posts else 0
    top_commented = [
        {"post_id": p.telegram_post_id, "text_preview": (p.text or "")[:80], "replies": p.replies_count}
        for p in posts[:3]
        if p.replies_count > 0
    ]

    # Members
    members = (await db.execute(
        select(ChannelMember).where(ChannelMember.channel_id == channel.id).limit(200)
    )).scalars().all()

    week_ago = _utcnow() - timedelta(days=7)
    joins_7d = sum(1 for m in members if m.joined_at and m.joined_at >= week_ago)

    leaves = (await db.execute(
        select(ChannelAdminLog).where(
            ChannelAdminLog.channel_id == channel.id,
            ChannelAdminLog.event_type == "leave",
            ChannelAdminLog.event_date >= week_ago,
        )
    )).scalars().all()
    leaves_7d = len(leaves)

    # Invite links
    invite_links = (await db.execute(
        select(ChannelInviteLink)
        .where(ChannelInviteLink.channel_id == channel.id)
        .order_by(ChannelInviteLink.usage_count.desc())
    )).scalars().all()

    # Post details
    total_saves = sum(p.saves_count for p in posts)
    avg_saves = round(total_saves / len(posts), 1) if posts else 0

    reactions_agg: dict[str, int] = {}
    for p in posts:
        if p.reactions_detail:
            for emoji, count in p.reactions_detail.items():
                reactions_agg[emoji] = reactions_agg.get(emoji, 0) + count

    return {
        "bot_connected": True,
        "telethon_available": True,
        "fetched_at": channel.extended_fetched_at.isoformat() if channel.extended_fetched_at else None,
        "comments": {
            "total": total_replies,
            "avg_per_post": avg_replies,
            "top_posts": top_commented,
        },
        "members": {
            "total": channel.subscribers_count,
            "sample": [
                {
                    "username": m.username,
                    "first_name": m.first_name,
                    "joined_at": m.joined_at.isoformat() if m.joined_at else None,
                }
                for m in members[:50]
            ],
            "joins_7d": joins_7d,
            "leaves_7d": leaves_7d,
            "net_growth_7d": joins_7d - leaves_7d,
        },
        "traffic_sources": {
            "invite_links": [
                {"link": lnk.link, "usage_count": lnk.usage_count, "creator_id": lnk.creator_id}
                for lnk in invite_links
            ],
        },
        "post_details": {
            "avg_saves": avg_saves,
            "avg_replies": avg_replies,
            "reactions_breakdown": dict(sorted(reactions_agg.items(), key=lambda x: -x[1])[:20]),
        },
    }
