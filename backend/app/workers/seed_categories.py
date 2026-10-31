"""Seed channel_categories table from fixtures/categories.json on first boot."""

import json
import logging
from pathlib import Path

from sqlalchemy import select

from app.core.database import async_session
from app.models.category import ChannelCategory

logger = logging.getLogger(__name__)

FIXTURES_PATH = Path(__file__).parent.parent / "fixtures" / "categories.json"


async def seed_categories() -> None:
    """Insert categories from fixtures if table is empty."""
    async with async_session() as db:
        result = await db.execute(select(ChannelCategory).limit(1))
        if result.scalar_one_or_none() is not None:
            logger.info("Categories already seeded — skipping")
            return

        data = json.loads(FIXTURES_PATH.read_text(encoding="utf-8"))
        for item in data:
            db.add(ChannelCategory(name=item["name"], slug=item["slug"]))

        await db.commit()
        logger.info("Seeded %d categories", len(data))
