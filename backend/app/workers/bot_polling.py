"""Background task: poll for bot admin status changes via my_chat_member updates."""

import asyncio
import logging

from telegram import Bot, Update
from telegram.error import TelegramError
from sqlalchemy import select

from app.core.config import settings
from app.core.database import async_session
from app.models.channel import Channel

logger = logging.getLogger(__name__)


async def handle_my_chat_member(update: Update) -> None:
    """Process my_chat_member update — bot added/removed as admin."""
    chat_member = update.my_chat_member
    if chat_member is None:
        return

    chat = chat_member.chat
    new_status = chat_member.new_chat_member.status
    username = chat.username

    if not username:
        logger.info("Bot status changed in chat without username, skipping")
        return

    is_admin = new_status in ("administrator", "creator")
    logger.info(
        "Bot %s in @%s (status: %s)",
        "added as admin" if is_admin else "removed",
        username,
        new_status,
    )

    async with async_session() as db:
        result = await db.execute(
            select(Channel).where(Channel.username == username.lower())
        )
        channel = result.scalar_one_or_none()
        if channel:
            channel.bot_is_admin = is_admin
            await db.commit()
            logger.info("Updated bot_is_admin=%s for @%s", is_admin, username)
        else:
            logger.info("Channel @%s not in DB yet — will be set on first analyze", username)


async def start_bot_polling() -> None:
    """Start polling for bot updates in background."""
    if not settings.BOT_TOKEN:
        logger.info("BOT_TOKEN not set — bot polling disabled")
        return

    bot = Bot(token=settings.BOT_TOKEN)
    offset = 0
    logger.info("Bot polling started")

    while True:
        try:
            updates = await bot.get_updates(
                offset=offset,
                timeout=30,
                allowed_updates=["my_chat_member"],
            )
            for update in updates:
                offset = update.update_id + 1
                await handle_my_chat_member(update)
        except TelegramError as e:
            logger.error("Bot polling error: %s", e)
            await asyncio.sleep(5)
        except Exception as e:
            logger.error("Bot polling unexpected error: %s", e)
            await asyncio.sleep(10)
