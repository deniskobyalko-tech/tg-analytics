"""Bot API client for extended channel statistics."""

import logging

from telegram import Bot
from telegram.error import TelegramError

from app.core.config import settings

logger = logging.getLogger(__name__)

_bot: Bot | None = None


def get_bot() -> Bot | None:
    """Get Bot instance. Returns None if BOT_TOKEN not configured."""
    global _bot
    if not settings.BOT_TOKEN:
        return None
    if _bot is None:
        _bot = Bot(token=settings.BOT_TOKEN)
    return _bot


def parse_reactions_detail(reactions: list[dict] | None) -> dict[str, int]:
    """Parse Bot API reaction objects into {emoji: count} dict."""
    if not reactions:
        return {}
    result = {}
    for r in reactions:
        emoji = r.get("emoji", "")
        count = r.get("total_count", 0)
        if emoji and count:
            result[emoji] = count
    return result


async def check_bot_is_admin(username: str) -> tuple[bool, int | None]:
    """Check if our bot is an admin in the given channel.

    Returns (is_admin, chat_id) — chat_id is the numeric Telegram ID.
    """
    bot = get_bot()
    if bot is None:
        return False, None
    try:
        chat = await bot.get_chat(chat_id=f"@{username}")
        me = await bot.get_me()
        member = await bot.get_chat_member(chat_id=chat.id, user_id=me.id)
        is_admin = member.status in ("administrator", "creator")
        return is_admin, chat.id
    except TelegramError as e:
        logger.warning("Failed to check bot admin status for @%s: %s", username, e)
        return False, None


async def fetch_bot_channel_data(chat_id: int | str) -> dict:
    """Fetch extended data via Bot API: member count."""
    bot = get_bot()
    if bot is None:
        return {}

    try:
        member_count = await bot.get_chat_member_count(chat_id=chat_id)
    except TelegramError:
        member_count = 0

    return {"member_count": member_count}
