import asyncio
import logging
from datetime import date, datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.models.channel import Channel, ChannelSnapshot
from app.services.scraper import fetch_channel_preview
from app.services.analyzer import calculate_er

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


async def update_all_channels():
    async with async_session() as db:
        result = await db.execute(
            select(Channel).order_by(Channel.last_scraped_at.asc()).limit(50)
        )
        channels = result.scalars().all()

        for channel in channels:
            try:
                preview = await fetch_channel_preview(channel.username)
                channel.subscribers_count = preview["subscribers_count"]
                channel.title = preview["title"] or channel.title
                channel.avatar_url = preview["avatar_url"] or channel.avatar_url
                channel.er = calculate_er(channel.avg_views, channel.subscribers_count)
                channel.last_scraped_at = _utcnow()

                today = date.today()
                existing = await db.execute(
                    select(ChannelSnapshot).where(
                        ChannelSnapshot.channel_id == channel.id,
                        ChannelSnapshot.date == today,
                    )
                )
                snapshot = existing.scalar_one_or_none()
                if snapshot is None:
                    snapshot = ChannelSnapshot(
                        channel_id=channel.id,
                        date=today,
                        subscribers=channel.subscribers_count,
                        avg_views=channel.avg_views,
                        er=channel.er,
                        posts_count=0,
                    )
                    db.add(snapshot)
                else:
                    snapshot.subscribers = channel.subscribers_count
                    snapshot.avg_views = channel.avg_views
                    snapshot.er = channel.er

                await db.commit()
                logger.info(f"Updated {channel.username}")
                await asyncio.sleep(12)

            except Exception as e:
                logger.error(f"Failed to update {channel.username}: {e}")
                continue
