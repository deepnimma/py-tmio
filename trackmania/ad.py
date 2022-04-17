import json
import logging
from contextlib import suppress
from typing import Dict, List

import redis
from typing_extensions import Self

from trackmania.errors import TMIOException

from .api import _APIClient
from .config import Client
from .constants import _TMIO

_log = logging.getLogger(__name__)

__all__ = ("Ad",)


async def _get_ad_list() -> List[Dict]:
    ad_list = []

    _log.debug("Getting all ads")
    cache_client = Client._get_cache_client()
    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        if cache_client.exists("ads"):
            _log.debug("Found all ads in cache")
            ads = json.loads(cache_client.get("ads").decode("utf-8"))
            for ad_dict in ads.get("ads"):
                ad_list.append(ad_dict)
            return ad_list

    api_client = _APIClient()
    all_ads = await api_client.get(_TMIO.build([_TMIO.TABS.ADS]))
    await api_client.close()

    with suppress(KeyError, TypeError):
        raise TMIOException(all_ads["error"])
    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        _log.debug("Caching all ads for 12hours")
        cache_client.set("ads", json.dumps(all_ads), ex=43200)

    for ad_dict in all_ads.get("ads"):
        ad_list.append(ad_dict)

    return ad_list


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
        The type of the ad.
        Can be "nadeo" or "ugc". "Nadeo" is for official advertisements while "UGC" is for user generated content.
    url : str
        URL set for the ad by the uploaders of the ad.
    img2x3 : str
        Link to where the 2x3 image of the ad is stored.
        Can be empty if it does not exist.
    img16x9 : str
        Link to where the 16x9 image of the ad is stored.
        Can be empty if it does not exist.
    img64x10 : str
        Link to where the 64x10 image of the ad is stored.
        Can be empty if it does not exist.
    media : str
        Link to get the media of the ad.
    display_format : str
        The display format of the ad.
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
        """Constructor Function."""
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
    def _from_dict(cls: Self, raw: Dict) -> Self:
        uid = raw.get("uid")
        name = raw.get("name")
        type = raw.get("type")
        url = raw.get("url")
        img2x3 = raw.get("img2x3")
        img16x9 = raw.get("img16x9")
        img64x10 = raw.get("img64x10")
        media = raw.get("media")
        display_format = raw.get("displayformat")

        args = [uid, name, type, url, img2x3, img16x9, img64x10, media, display_format]
        return cls(*args)

    @classmethod
    async def list_ads(cls) -> List[Self]:
        """
        .. versionadded :: 0.3.0
        .. versionchanged :: 0.4.0
            Changed to classmethod

        Lists all ads currently in trackmania.

        Returns
        -------
        :class:`List[Self]`
            All the Ads

        Raises
        ------
        :class:`TMIOException`
            If an unexpected error occurs.
        """
        _log.info("Listing all Ads")
        try:
            all_ads = await _get_ad_list()
        except TMIOException as excp:
            raise TMIOException("An Unexpected Error Occured") from excp

        ad_list = []
        for ad in all_ads:
            ad_list.append(cls._from_dict(ad))
        return ad_list

    @classmethod
    async def get_ad(cls, ad_uid: str) -> Self | None:
        """
        .. versionadded :: 0.3.0
        .. versionchanged :: 0.4.0
            Changed to classmethod

        Gets an ad by its unique ID.

        Parameters
        ----------
        ad_uid : str
            The unique ID of the ad

        Returns
        -------
        :class:`Self`
            The ad
        """
        _log.info("Getting Ad with UID: %s", ad_uid)
        all_ads = await cls.list_ads()
        for ad in all_ads:
            if ad.uid == ad_uid:
                _log.debug("Ad with UID %s found", ad_uid)
                return ad

        _log.debug("No Ad With UID %s found", ad_uid)
        return None
