import json
from contextlib import suppress
from datetime import date, datetime
from typing import Dict, List

import redis

from trackmania.structures.cotd import PlayerCOTD


async def get_player_cotd(page: int = 0):
    """
    Gets the player cotd data.

    Parameters
    ----------
    page : int, optional
        Which page of cotd data to get. If set to -1 it returns ALL cotd data. WARNING: Uses a lot of requests.
        defaults to 0

    Returns
    -------
    _type_
        _description_
    """

    # Will start later.
    return -1
