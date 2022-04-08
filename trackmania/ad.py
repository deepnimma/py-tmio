import json
import logging
from contextlib import suppress
from typing import Dict, List

import redis

from trackmania.errors import TMIOException

from .api import _APIClient
from .config import Client
from .constants import _TMIO

_log = logging.getLogger(__name__)

__all__ = ("Ad",)


class Ad:
    """
    .. versionadded :: 0.3.0

    Represents an Ad in Trackmania

    Parameters
    ----------
    uid : str
        The unique ID of the ad
    name : str
        The name of the ad
    type : str
        The type of the ad
    url : str
        URL set for the ad
    img2x3 : str
        Link to get the 2x3 image of the ad
    img16x9 : str
        Link to get the 16x9 image of the ad
    img64x10 : str
        Link to get the 64x10 image of the ad
    media : str
        Link to get the media of the ad
    display_format : str
        The display format of the ad
    """

    def __init__(
        self,
        uid: str,
        name: str,
        type: str,
        url: str,
        img2x3: str,
        img16x9: str,
        img64x10: str,
        media: str,
        display_format: str,
    ):
        self.uid = uid
        self.name = name
        self.type = type
        self.url = url
        self.img2x3 = img2x3
        self.img16x9 = img16x9
        self.img64x10 = img64x10
        self.media = media
        self.display_format = display_format

    @classmethod
    def _from_dict(cls, raw: Dict):
        _log.debug("Creating an Ad object from given dictionary")

        uid = raw["uid"]
        name = raw["name"]
        type = raw["type"]
        img2x3 = raw["img2x3"]
        img16x9 = raw["img16x9"]
        img64x10 = raw["img64x10"]
        media = raw["media"]
        display_format = raw["displayformat"]

        return cls(
            uid,
            name,
            type,
            img2x3,
            img16x9,
            img64x10,
            media,
            display_format,
        )

    @staticmethod
    async def list() -> List:
        """
        .. versionadded :: 0.3.0

        Lists all ads currently in trackmania.

        Returns
        -------
        :class:`List[Ad]`
            All the ads.
        """
        _log.debug("Getting all ads")

        cache_client = Client._get_cache_client()

        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            if cache_client.exists("ads"):
                _log.debug("Found all ads in cache")
                ads = json.loads(cache_client.get("ads").decode("utf-8"))

                bads = []
                for ad in ads["ads"]:
                    bads.append(Ad._from_dict(ad))

                return bads

        api_client = _APIClient()
        all_ads = await api_client.get(_TMIO.build([_TMIO.TABS.ADS]))
        await api_client.close()

        with suppress(KeyError, TypeError):
            raise TMIOException(all_ads["error"])
        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            _log.debug("Caching all ads for 12hours")
            cache_client.set("ads", json.dumps(all_ads), ex=43200)

        bads = []
        for ad in all_ads["ads"]:
            bads.append(Ad._from_dict(ad))

        return bads

    @staticmethod
    async def get(ad_uid: str):
        """
        .. versionadded :: 0.3.0

        Gets an ad using its uid.

        Parameters
        ----------
        ad_uid : str
            The uid of the ad

        Returns
        -------
        :class:`Ad` | None
            The ad with the specific uid.
        """
        _log.debug("Getting ad with uid: %s", ad_uid)

        ads = await Ad.list()

        for ad in ads:
            if ad.uid == ad_uid:
                return ad

        _log.debug("No Ad found with uid %s", ad_uid)
        return None
