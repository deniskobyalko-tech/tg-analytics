"""Periodic worker: compute topic + category similarity for all channel pairs."""

import logging
from itertools import combinations

from sqlalchemy import delete, select

from app.core.database import async_session
from app.models.channel import Channel
from app.models.similarity import ChannelSimilarity
from app.services.similarity import compute_topic_similarity

logger = logging.getLogger(__name__)

TOPIC_THRESHOLD = 0.05  # store even weak topic similarities
CATEGORY_SCORE = 0.3  # base score for same-category channels


async def compute_all_similarities() -> None:
    """Recompute similarities for every channel pair in the DB."""
    async with async_session() as db:
        result = await db.execute(select(Channel))
        channels = result.scalars().all()

        if len(channels) < 2:
            logger.info("Less than 2 channels — skipping similarity computation")
            return

        # Clear stale data
        await db.execute(delete(ChannelSimilarity))

        count = 0
        for ch_a, ch_b in combinations(channels, 2):
            # Topic similarity (keyword overlap)
            topic_score = compute_topic_similarity(
                ch_a.title, ch_a.description,
                ch_b.title, ch_b.description,
            )

            # Category bonus: channels in same category get a base score
            category_bonus = 0.0
            if (
                ch_a.category_id is not None
                and ch_b.category_id is not None
                and ch_a.category_id == ch_b.category_id
            ):
                category_bonus = CATEGORY_SCORE

            final_score = min(round(topic_score + category_bonus, 3), 1.0)

            if final_score > TOPIC_THRESHOLD:
                match_type = "category" if category_bonus > topic_score else "topic"
                db.add(ChannelSimilarity(
                    channel_id=ch_a.id,
                    similar_channel_id=ch_b.id,
                    score=final_score,
                    match_type=match_type,
                ))
                db.add(ChannelSimilarity(
                    channel_id=ch_b.id,
                    similar_channel_id=ch_a.id,
                    score=final_score,
                    match_type=match_type,
                ))
                count += 1

        await db.commit()
        logger.info("Computed similarities: %d pairs from %d channels", count, len(channels))
