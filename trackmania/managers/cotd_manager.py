import json
from contextlib import suppress
from datetime import date, datetime
from typing import Dict, List

import redis

from ..config import Client
from ..structures.cotd import PlayerCOTD


async def get_player_cotd(page: int = 0) -> PlayerCOTD:
    """
    Gets the player cotd data.

    Parameters
    ----------
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

    # Will start later.
    return -1
