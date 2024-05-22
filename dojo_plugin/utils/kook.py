from logging import getLogger
from typing import TypedDict, Union

import requests, asyncio
from CTFd.cache import cache
from flask import url_for
from khl import Bot, Channel, GuildUser

from ..config import KOOK_CLIENT_ID, KOOK_GUILD_ID, KOOK_TOKEN, KOOK_CLIENT_SECRET
from ..models import KookUsers

KOOK_BASE_URL = "https://www.kookapp.cn/api"


async def _send_message(message, channel_id, logger=getLogger(__name__)) -> None:
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

def send_message(message, channel_id, logger=getLogger(__name__)) -> None:
    asyncio.run(_send_message(message, channel_id, logger=logger))


async def _get_kook_user(user_id, logger=getLogger(__name__)) -> Union[GuildUser, None]:
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

def get_kook_user(user_id, logger=getLogger(__name__)) -> Union[GuildUser, None]:
    return asyncio.run(_get_kook_user(user_id, logger=logger))

class KookUser(TypedDict):
    id: str
    username: str
    identify_num: str
    online: bool
    os: str
    status: int
    avatar: str
    banner: str
    bot: bool
    mobile_verified: bool
    mobile_prefix: str
    mobile: str
    invited_count: int


def get_kook_user_from_auth_code(code) -> KookUser:
    if not KOOK_TOKEN:
        raise RuntimeError("KOOK_TOKEN is not set")
    # get access token
    url = f"{KOOK_BASE_URL}/oauth2/token"
    resp = requests.post(
        url,
        json={
            "grant_type": "authorization_code",
            "client_id": KOOK_CLIENT_ID,
            "client_secret": KOOK_CLIENT_SECRET,
            "code": code,
            "redirect_uri": url_for("kook.kook_redirect", _external=True),
        },
    )

    if resp.status_code != 200:
        raise RuntimeError(f"get access token failed: {resp.text}")

    access_token = resp.json()["access_token"]

    # get user info
    url = f"{KOOK_BASE_URL}/v3/user/me"
    resp = requests.get(url, headers={"Authorization": f"Bearer {access_token}"})
    if resp.status_code != 200:
        raise RuntimeError(f"get user info failed: {resp.text}")

    d = resp.json()
    if d["code"] != 0:
        raise RuntimeError(f"get user info failed: {d}")

    return d["data"]
