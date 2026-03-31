import asyncio
import logging
from pathlib import Path

from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.tl.functions.channels import GetFullChannelRequest

from app.core.config import settings

logger = logging.getLogger(__name__)

_client: TelegramClient | None = None
SESSION_PATH = Path("/app/data/session")


async def get_client() -> TelegramClient:
    global _client
    if _client is None or not _client.is_connected():
        _client = TelegramClient(
            str(SESSION_PATH),
            settings.TELEGRAM_API_ID,
            settings.TELEGRAM_API_HASH,
        )
        await _client.start(phone=settings.TELEGRAM_PHONE)
    return _client


def extract_channel_stats(entity) -> dict:
    return {
        "telegram_id": entity.id,
        "title": entity.title,
        "username": getattr(entity, "username", None),
        "subscribers_count": getattr(entity, "participants_count", 0) or 0,
    }


def extract_post_data(msg) -> dict:
    reactions_count = 0
    if msg.reactions:
        if hasattr(msg.reactions, "results"):
            reactions_count = sum(r.count for r in msg.reactions.results)

    return {
        "telegram_post_id": msg.id,
        "text": msg.message,
        "date": msg.date,
        "views": msg.views or 0,
        "forwards": msg.forwards or 0,
        "reactions": reactions_count,
    }


async def fetch_channel_data(username: str) -> dict:
    client = await get_client()
    try:
        entity = await client.get_entity(username)
        full = await client(GetFullChannelRequest(entity))
        stats = extract_channel_stats(entity)
        stats["description"] = full.full_chat.about

        posts = []
        async for msg in client.iter_messages(entity, limit=100):
            if msg.message:
                posts.append(extract_post_data(msg))

        if posts:
            stats["avg_views"] = sum(p["views"] for p in posts) // len(posts)
            dates = [p["date"] for p in posts if p["date"]]
            if len(dates) >= 2:
                span_days = (max(dates) - min(dates)).days or 1
                stats["posts_per_week"] = round(len(posts) / span_days * 7, 1)
            else:
                stats["posts_per_week"] = 0.0
        else:
            stats["avg_views"] = 0
            stats["posts_per_week"] = 0.0

        return {"channel": stats, "posts": posts}

    except FloodWaitError as e:
        logger.warning(f"FloodWait: sleeping {e.seconds}s")
        await asyncio.sleep(e.seconds)
        return await fetch_channel_data(username)
