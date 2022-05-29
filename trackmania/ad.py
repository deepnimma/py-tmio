import logging
from contextlib import suppress

from typing_extensions import Self

from trackmania.errors import TMIOException

from ._util import _regex_it
from .api import _APIClient
from .base import AdObject
from .config import get_from_cache, set_in_cache
from .constants import _TMIO

_log = logging.getLogger(__name__)

__all__ = ("Ad",)


async def _get_ad_list() -> list[dict]:
    ad_list = []

    _log.debug("Getting all ads")
    ads = get_from_cache("ads")
    if ads is not None:
        for ad_dict in ads.get("ads"):
            ad_list.append(ad_dict)
        return ad_list

    api_client = _APIClient()
    all_ads = await api_client.get(_TMIO.build([_TMIO.TABS.ADS]))
    await api_client.close()

    with suppress(KeyError, TypeError):
        raise TMIOException(all_ads["error"])

    set_in_cache("ads", all_ads, ex=43200)

    for ad_dict in all_ads.get("ads"):
        ad_list.append(ad_dict)

    return ad_list


class Ad(AdObject):
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
    def _from_dict(cls: Self, raw: dict) -> Self:
        uid = raw.get("uid")
        name = _regex_it(raw.get("name"))
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
    async def list_ads(cls) -> list[Self]:
        """
        .. versionadded :: 0.3.0
        .. versionchanged :: 0.4.0
            Changed to classmethod

        Lists all ads currently in trackmania.

        Returns
        -------
        :class:`list[Self]`
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
