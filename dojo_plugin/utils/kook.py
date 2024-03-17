from logging import getLogger

from khl import Bot, Channel, GuildUser

from ..config import KOOK_GUILD_ID, KOOK_TOKEN
from ..models import KookUsers


async def send_message(message, channel_id, logger=getLogger(__name__)) -> None:
    if KOOK_TOKEN is None:
        logger.error("KOOK_TOKEN is not set")
        return
    bot = Bot(token=KOOK_TOKEN)
    ch = await bot.client.fetch_public_channel(channel_id)
    if ch is None:
        logger.error(f"channel {channel_id} not found")
        return
    logger.debug(f"send message to channel {channel_id}")
    await ch.send(message)


async def get_kook_user(user_id, logger=getLogger(__name__)) -> GuildUser | None:
    if not KOOK_TOKEN:
        logger.error("KOOK_TOKEN is not set")
        return
    if not KOOK_GUILD_ID:
        logger.error("KOOK_GUILD_ID is not set")
        return

    kook_user = KookUsers.query.filter_by(user_id=user_id).first()
    if not kook_user:
        logger.error(f"Kook user {user_id} not found")
        return

    bot = Bot(token=KOOK_TOKEN)
    guild = await bot.client.fetch_guild(KOOK_GUILD_ID)
    result = await guild.fetch_user(kook_user.kook_id)
    return result
