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


# --- Extended stats helpers ---

EVENT_TYPE_MAP = {
    "ChannelAdminLogEventActionParticipantJoin": "join",
    "ChannelAdminLogEventActionParticipantLeave": "leave",
    "ChannelAdminLogEventActionEditMessage": "edit_message",
    "ChannelAdminLogEventActionDeleteMessage": "delete_message",
    "ChannelAdminLogEventActionUpdatePinned": "pin",
}


def parse_admin_log_event(event) -> dict:
    """Parse a Telethon admin log event into a flat dict."""
    action_class = event.action.__class__.__name__
    event_type = EVENT_TYPE_MAP.get(action_class, action_class)
    return {
        "event_type": event_type,
        "user_id": event.user_id,
        "event_date": event.date.replace(tzinfo=None) if event.date else None,
        "data": None,
    }


def parse_participant(user, participant) -> dict:
    """Parse a Telethon user + participant into a flat dict."""
    joined = getattr(participant, "date", None)
    if joined and joined.tzinfo:
        joined = joined.replace(tzinfo=None)
    return {
        "telegram_user_id": user.id,
        "username": getattr(user, "username", None),
        "first_name": getattr(user, "first_name", None),
        "joined_at": joined,
    }


async def fetch_admin_log(username: str, limit: int = 100) -> list[dict]:
    """Fetch admin log events (join/leave) for a channel."""
    client = await get_client()
    try:
        from telethon.tl.functions.channels import GetAdminLogRequest
        from telethon.tl.types import ChannelAdminLogEventsFilter

        entity = await client.get_entity(username)
        result = await client(GetAdminLogRequest(
            channel=entity,
            q="",
            min_id=0,
            max_id=0,
            limit=limit,
            events_filter=ChannelAdminLogEventsFilter(join=True, leave=True),
            admins=[],
        ))
        return [parse_admin_log_event(e) for e in result.events]
    except Exception as e:
        logger.error("Failed to fetch admin log for %s: %s", username, e)
        return []


async def fetch_participants(username: str, limit: int = 200) -> list[dict]:
    """Fetch channel participants (up to limit)."""
    client = await get_client()
    try:
        entity = await client.get_entity(username)
        participants = await client.get_participants(entity, limit=limit)
        return [
            parse_participant(p, p.participant)
            for p in participants
            if hasattr(p, "participant")
        ]
    except Exception as e:
        logger.error("Failed to fetch participants for %s: %s", username, e)
        return []


async def fetch_invite_links(username: str) -> list[dict]:
    """Fetch exported invite links for a channel."""
    client = await get_client()
    try:
        from telethon.tl.functions.messages import GetExportedChatInvitesRequest

        entity = await client.get_entity(username)
        me = await client.get_me()
        result = await client(GetExportedChatInvitesRequest(
            peer=entity,
            admin_id=me,
            limit=50,
            revoked=False,
        ))
        return [
            {
                "link": inv.link,
                "creator_id": getattr(inv, "admin_id", None),
                "usage_count": inv.usage or 0,
            }
            for inv in result.invites
        ]
    except Exception as e:
        logger.error("Failed to fetch invite links for %s: %s", username, e)
        return []
