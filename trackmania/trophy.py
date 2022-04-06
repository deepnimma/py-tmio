import json
import logging
from contextlib import suppress
from datetime import datetime
from types import NoneType
from typing import Dict, List

import redis

from .api import APIClient
from .config import Client
from .constants import TMIO
from .errors import InvalidIDError, InvalidTrophyNumber, TMIOException

_log = logging.getLogger(__name__)

__all__ = ("PlayerTrophies",)


class PlayerTrophies:
    """
    .. versionadded :: 0.1.0

    Represents Player Trophies

    Parameters
    ----------
    echelon : int
        The trophy echelon of the player.
    last_change : str
        The date of the last change of the player's self.
    points : ints: int
        The number of points of the player.
    trophies : :class:`List[int]`
        The number of trophies of the player.
    player_id : str | :class:`NoneType`, optional
        The Trackmania ID of the player
    """

    def __init__(
        self,
        echelon: int,
        last_change: datetime,
        points: int,
        trophies: List[int],
        player_id: str | NoneType = None,
    ):
        """Constructor for the class."""
        self.echelon = echelon
        self._last_change = last_change
        self.points = points
        self.trophies = trophies
        self._player_id = player_id

    @classmethod
    def _from_dict(cls, raw_trophy_data: Dict, player_id: str):
        """
        Creates a :class:`PlayerTrophies` object from the given dictionary.

        Parameters
        ----------
        raw_trophy_data : :class:`Dict`
            The raw trophy data to parse.
        player_id : str
            The player ID to set.
        Returns
        -------
        :class:`PlayerTrophies`
            The parsed trophy data.
        """
        _log.debug(f"Creating a PlayerTrophies class from the given dictionary.")

        return cls(
            echelon=raw_trophy_data["echelon"],
            last_change=datetime.strptime(
                raw_trophy_data["timestamp"], "%Y-%m-%dT%H:%M:%S+00:00"
            ),
            points=raw_trophy_data["points"],
            trophies=raw_trophy_data["counts"],
            player_id=player_id,
        )

    @property
    def last_change(self):
        """Last change property."""
        return self._last_change

    @property
    def player_id(self):
        """player_id property"""
        return self._player_id

    def set_id(self, player_id: str):
        """Setter for player_id"""
        self._player_id = player_id

    def trophy(self, number: int) -> int:
        """
        .. versionadded :: 0.3.0

        Returns the trophies by tier.

        Parameters
        ----------
        number : int
            The trophy number, from 1 (T1) to 9 (T9).
        Returns
        -------
        int
            the number of trophies for that specific tier.
        """
        _log.debug(f"Returning trophy T{number} for player {self.player_id}")

        if number > 9 or number < 1:
            raise InvalidTrophyNumber(
                "Trophy Number cannot be less than 1 or greater than 9"
            )

        return self.trophies[number - 1]

    def score(self) -> int:
        """Returns the trophy score of the player."""
        return (
            0
            + self.trophy(1) * 1
            + self.trophy(2) * 10
            + self.trophy(3) * 100
            + self.trophy(4) * 1_000
            + self.trophy(5) * 10_000
            + self.trophy(6) * 100_000
            + self.trophy(7) * 1_000_000
            + self.trophy(8) * 10_000_000
        )

    async def history(self, page: int = 0) -> Dict:
        """
        .. versionadded :: 0.3.0

        Retrieves Trophy Gain and Loss history of a player.

        Parameters
        ----------
        page : int, optional
            page number of trophy history, by default 0
        Returns
        -------
        :class:`Dict`
            Trophy history data.
        Raises
        ------
        InvalidIDError
            If an ID has not been set for the object.
        InvalidIDError
            If an invalid id has been set for the object.
        """
        _log.debug(f"Getting Trophy Leaderboard for Page: {page}")

        cache_client = redis.Redis(
            host=Client.REDIS_HOST,
            port=Client.REDIS_PORT,
            db=Client.REDIS_DB,
            password=Client.REDIS_PASSWORD,
        )

        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            if cache_client.exists(f"trophy:{page}"):
                _log.debug(f"Found trophy leaderboard for page {page} in cache")
                return json.loads(cache_client.get(f"trophy:{page}").decode("utf-8"))[
                    "gains"
                ]

        api_client = APIClient()

        if self.player_id is None:
            raise InvalidIDError("ID Has not been set for the Object")

        history = await api_client.get(
            TMIO.build(
                [TMIO.TABS.PLAYER, self.player_id, TMIO.TABS.TROPHIES, str(page)]
            )
        )

        await api_client.close()

        with suppress(KeyError, TypeError):
            _log.error("This is a trackmania.io error")
            raise TMIOException(history["error"])
        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            _log.debug(f"Caching trophy history for page: {page}")
            cache_client.set(f"trophy:{page}", json.dumps(history), ex=3600)

        return history["gains"]

    @staticmethod
    async def top(page: int = 0) -> Dict:
        """
        .. versionadded :: 0.3.0

        Get's the top players ranked by trophies

        Parameters
        ----------
        page : int, optional
            The page of the leaderboards, by default 0

        Returns
        -------
        Dict
            The players
        """
        _log.debug(f"Getting Page {page} of Trophy Leaderboards")

        cache_client = redis.Redis(
            host=Client.REDIS_HOST,
            port=Client.REDIS_PORT,
            db=Client.REDIS_DB,
            password=Client.REDIS_PASSWORD,
        )

        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            if cache_client.exists(f"trophies:{page}"):
                _log.debug(f"Found trophy leaderboard for page {page} in cache")
                return json.loads(cache_client.get(f"trophies:{page}").decode("utf-8"))[
                    "ranks"
                ]

        api_client = APIClient()

        top_trophies = await api_client.get(
            TMIO.build([TMIO.TABS.TOP_TROPHIES, str(page)])
        )

        await api_client.close()

        with suppress(KeyError, TypeError):
            _log.error("This is a trackmania.io error")
            raise TMIOException(top_trophies["error"])
        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            _log.debug(f"Caching trophy leaderboard for page: {page}")
            cache_client.set(f"trophies:{page}", json.dumps(top_trophies), ex=3600)

        return top_trophies["ranks"]
