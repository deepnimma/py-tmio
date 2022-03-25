import json
from contextlib import suppress

import redis

from ..api import APIClient
from ..config import Client
from ..constants import TMIO
from ..structures.ad import Ad
from ..util import ad_parsers


async def get_ad(ad_uid: str) -> Ad:
    """
    Retrieves the Trackmania Maniapub of the given ad uid.

    Parameters
    ----------
    ad_uid : str
        The ad uid

    Returns
    -------
    :class:`Ad`
        The maniapub.
    """
    cache_client = redis.Redis(host=Client.REDIS_HOST, port=Client.REDIS_PORT)

    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        if cache_client.exists(f"ad|{ad_uid}"):
            return ad_parsers.parse_ad(json.loads(cache_client.get(f"ad|{ad_uid}")))

    api_client = APIClient()
    ad_resp = await api_client.get(TMIO.build([TMIO.TABS.ADS]))
    await api_client.close()

    if len(ad_resp) > 1:
        for i, ad in enumerate(ad_resp["ads"]):
            if ad["uid"] == ad_uid:
                req_ad = ad_resp[i]
                break

    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        cache_client.set(f"ad|{ad_uid}", json.dumps(req_ad))

    return ad_parsers.parse_ad(req_ad)
