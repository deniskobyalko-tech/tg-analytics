"""Periodic worker: compute audience overlap via forward-graph heuristic."""

import logging
import re
from itertools import combinations

from sqlalchemy import delete, select

from app.core.database import async_session
from app.models.channel import Channel
from app.models.post import Post
from app.models.similarity import AudienceOverlap

logger = logging.getLogger(__name__)


def compute_forward_overlap(forwards_a: set[str], forwards_b: set[str]) -> float:
    """Jaccard similarity between two forward-source sets."""
    if not forwards_a and not forwards_b:
        return 0.0
    union = forwards_a | forwards_b
    if not union:
        return 0.0
    intersection = forwards_a & forwards_b
    return round(len(intersection) / len(union), 3)


async def compute_all_overlaps() -> None:
    """Recompute audience overlap for all channel pairs using forward graph."""
    async with async_session() as db:
        result = await db.execute(select(Channel))
        channels = result.scalars().all()

        if len(channels) < 2:
            logger.info("Less than 2 channels — skipping overlap computation")
            return

        # Build forward graph: channel_id -> set of forwarded-from usernames
        forward_map: dict[int, set[str]] = {}
        for ch in channels:
            posts_result = await db.execute(
                select(Post).where(Post.channel_id == ch.id)
            )
            posts = posts_result.scalars().all()

            forward_sources: set[str] = set()
            for p in posts:
                # Use fwd_from_channel field (filled by scraper/Telethon)
                if p.fwd_from_channel:
                    forward_sources.add(p.fwd_from_channel.lower())
                # Also extract @mentions from text as weak signal
                if p.text:
                    mentions = re.findall(r"@(\w{5,})", p.text)
                    forward_sources.update(m.lower() for m in mentions)
            forward_map[ch.id] = forward_sources

        # Clear stale data
        await db.execute(delete(AudienceOverlap))

        count = 0
        for ch_a, ch_b in combinations(channels, 2):
            overlap = compute_forward_overlap(
                forward_map.get(ch_a.id, set()),
                forward_map.get(ch_b.id, set()),
            )
            if overlap > 0.0:
                db.add(AudienceOverlap(
                    channel_a_id=ch_a.id,
                    channel_b_id=ch_b.id,
                    overlap_percent=round(overlap * 100, 1),
                ))
                count += 1

        await db.commit()
        logger.info("Computed audience overlaps: %d pairs from %d channels", count, len(channels))
