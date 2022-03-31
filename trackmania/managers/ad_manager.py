import json
from contextlib import suppress
import logging
from typing import Dict, List

import redis

from ..api import APIClient
from ..config import Client
from ..constants import TMIO
from ..structures.ad import Ad

_log = logging.getLogger(__name__)


async def get_ad(ad_uid: str) -> Ad:
    """
    .. versionadded:: 0.2.0

    Retrieves the Trackmania Maniapub of the given ad uid.

    Parameters
    ----------
    ad_uid : str
        The ad uid

    Returns
    -------
    :class:`Ad`
        The maniapub.

    Raises
    ------
    `ValueError`
        If given `ad_uid` is empty or :class:`NoneType`.
    `TypeError`
        If given `ad_uid` is not a string.
    """
    cache_client = redis.Redis(
        host=Client.REDIS_HOST,
        port=Client.REDIS_PORT,
        db=Client.REDIS_DB,
        password=Client.REDIS_PASSWORD,
    )

    if ad_uid == "" or ad_uid is None:
        raise ValueError("ad_uid cannot be NoneType or empty.")
    if not isinstance(ad_uid, str):
        raise TypeError("ad_uid must be a string.")

    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        if cache_client.exists(f"ad|{ad_uid}"):
            _log.debug(f"{ad_uid} was cached.")
            return _parse_ad(json.loads(cache_client.get(f"ad|{ad_uid}")))

    api_client = APIClient()
    _log.debug(f"Sending GET request to {TMIO.build([TMIO.TABS.ADS])}")
    ad_resp = await api_client.get(TMIO.build([TMIO.TABS.ADS]))
    await api_client.close()

    if len(ad_resp) > 1:
        for i, ad in enumerate(ad_resp["ads"]):
            if ad["uid"] == ad_uid:
                req_ad = ad_resp[i]
                break

    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        cache_client.set(f"ad|{ad_uid}", json.dumps(req_ad))
        _log.debug(f"Caching {ad_uid}.")

    return _parse_ad(req_ad)

async def list_ads() -> List[Ad]:
    """
    Lists all Ingame maniapubs.

    Returns
    -------
    :class:`List[Ad]`
        The List of Ingame Maniapubs
    """
    api_client = APIClient()
    _log.debug(f'Sending GET request to {TMIO.build([TMIO.TABS.ADS])}')
    ad_list_raw = await api_client.get(TMIO.build([TMIO.TABS.ADS]))
    await api_client.close()
    
    ad_list = list()
    for _, ad in enumerate(ad_list_raw["ads"]):
        ad_list.append(_parse_ad(ad))
        
    return ad_list

def _parse_ad(ad: Dict) -> Ad:
    """
    .. versionadded:: 0.2.0

    Parses an AD dict to an :class:`Ad` object.

    Parameters
    ----------
    ad : :class:`Dict`
        The ad data as a dict.

    Returns
    -------
    :class:`Ad`
        The ad data as an :class:`Ad` object.
    """
    ad_data = {
        "cp_image": ad["img64x10"],
        "display_format": ad["displayformat"],
        "image": ad["img16x9"],
        "media": ad["media"],
        "name": ad["name"],
        "type": ad["type"],
        "uid": ad["uid"],
        "url": ad["url"],
        "vertical_image": ad["img2x3"],
    }

    return Ad(**ad_data)
