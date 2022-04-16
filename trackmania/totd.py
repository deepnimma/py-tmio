import json
import logging
from contextlib import suppress
from datetime import datetime
from typing import Dict

import redis
from typing_extensions import Self

from trackmania.errors import InvalidTOTDDate, TMIOException

from .api import _APIClient
from .config import Client
from .constants import _TMIO
from .errors import TMIOException, TrackmaniaException
from .tmmap import TMMap

_log = logging.getLogger(__name__)

__all__ = ("TOTD",)


class TOTD:
    """
    .. versionadded :: 0.3.0

    Class that represents a TOTD

    Parameters
    ----------
    campaign_id : int
        The campaign's id
    leaderboard_uid : int
        The leaderboard's uid
    month_day : int
        The day of the month when the totd was played
    week_day : int
        The day of the week when the totd was played
    map : :class:`TMMap`
        The map that was played
    """

    def __init__(
        self,
        campaign_id: int,
        leaderboard_uid: int,
        month_day: int,
        week_day: int,
        mapobj: TMMap,
    ):
        self.campaign_id = campaign_id
        self.leaderboard_uid = leaderboard_uid
        self.month_day = month_day
        self.week_day = week_day
        self._mapobj = mapobj

    @classmethod
    def _from_dict(cls, raw: Dict):
        campaign_id = raw.get("campaignid")
        mapobj = TMMap._from_dict(raw.get("map"))
        week_day = raw.get("weekday")
        month_day = raw.get("monthday")
        leaderboard_uid = raw.get("leaderboarduid")

        return cls(
            campaign_id,
            leaderboard_uid,
            month_day,
            week_day,
            mapobj,
        )

    @staticmethod
    def _calculate_months(date: datetime) -> int:
        """
        .. versionadded :: 0.3.0

        Calculates the number of months from the given date to the current month.

        Parameters
        ----------
        date : datetime
            The date to calculate to

        Returns
        -------
        int
            How many months it has been
        """
        today = datetime.utcnow()
        today_month = today.month
        today_year = today.year

        months = (date.year - today_year) * 12
        return (months + date.month - today_month) * -1

    @property
    def map(self):
        """TMMap Property"""
        return self._mapobj

    @classmethod
    async def get_totd(cls: Self, date: datetime) -> Self:
        """
        .. versionadded :: 0.3.0

        Gets a map from the date provided.

        Parameters
        ----------
        date : datetime
            The date of the TOTD.

        Returns
        -------
        :class:`TOTD`
            The map
        """
        _log.debug("Getting TOTD for date: %s", date)

        cache_client = Client._get_cache_client()
        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            if cache_client.exists(f"totd:{date.year}:{date.month}:{date.day}"):
                _log.debug(
                    f"Found TOTD for date {date.day}:{date.month}:{date.year} in cache"
                )
                return cls._from_dict(
                    json.loads(
                        cache_client.get(
                            f"totd:{date.year}:{date.month}:{date.day}"
                        ).decode("utf-8")
                    )
                )

        api_client = _APIClient()
        all_totds = await api_client.get(
            _TMIO.build([_TMIO.TABS.TOTD, TOTD._calculate_months(date)])
        )
        await api_client.close()

        with suppress(KeyError, TypeError):
            raise TMIOException(all_totds["error"])

        if all_totds["lastday"] < date.day:
            raise InvalidTOTDDate(
                f"The date provided is not a valid TOTD date. The last day is {all_totds['lastday']}"
            )

        try:
            totd = all_totds["days"][date.day - 1]
        except (IndexError) as excp:
            raise InvalidTOTDDate("That TOTD Date is not correct.") from excp
        except (KeyError, TypeError) as excp:
            raise TrackmaniaException(
                f"Something Unexpected has occured. Please contact the developer of the Package.\nMessage: {excp}"
            ) from excp

        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            _log.debug(f"Caching TOTD for date {date.day}:{date.month}:{date.year}")
            cache_client.set(
                f"totd:{date.year}:{date.month}:{date.day}", json.dumps(totd)
            )

        return cls._from_dict(totd)

    @classmethod
    async def latest_totd(cls: Self) -> Self:
        """
        .. versionadded :: 0.3.3

        Gets the latest totd.

        Returns
        -------
        :class:`TOTD`
            The TOTD object.
        """
        today = datetime.utcnow()

        if today.hour > 17 and today.minute > 0:
            return await cls.get_totd(datetime.utcnow())
        else:
            return await cls.get_totd(datetime(today.year, today.month, today.day - 1))
