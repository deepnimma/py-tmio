import json
from contextlib import suppress
from datetime import date, datetime
from typing import Dict, List

import redis

from ..api import APIClient
from ..config import Client
from ..constants import TMIO
from ..structures.cotd import PlayerCOTD
from ..util.cotd_parsers import parse_cotd


async def get_player_cotd(player_id: str, page: int = 0) -> PlayerCOTD:
    """
    Gets the player cotd data.

    Parameters
    ----------
    player_id: str
        The player id.
    page : int, optional
        Which page of cotd data to get. If set to -1 it returns ALL cotd data. WARNING: Uses a lot of requests.
        defaults to 0

    Returns
    -------
    :class:`PlayerCOTD`
        The COTD Data as a :class:`PlayerCOTD` object.
    """
    cache_client = redis.Redis(
        host=Client.REDIS_HOST,
        port=Client.REDIS_PORT,
        db=Client.REDIS_DB,
        password=Client.REDIS_PASSWORD,
    )

    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        if cache_client.exists(f"{player_id}|cotd|{page}"):

            if page != -1:
                return PlayerCOTD(
                    **parse_cotd(
                        json.loads(cache_client.get(f"{player_id}|cotd|{page}"))
                    )
                )

    if page != -1:
        api_client = APIClient()
        cotd_page_resp = await api_client.get(
            TMIO.build([TMIO.TABS.PLAYER, player_id, TMIO.TABS.COTD, str(page)])
        )
        await api_client.close()

        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            cache_client.set(f"{player_id}|cotd|{page}", json.dumps(cotd_page_resp))

        return PlayerCOTD(**parse_cotd(cotd_page_resp))
