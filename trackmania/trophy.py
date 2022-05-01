import json
import logging
from contextlib import suppress
from datetime import datetime
from types import NoneType

import redis
from typing_extensions import Self

from ._util import _add_commas, _regex_it
from .api import _APIClient
from .config import Client, get_from_cache, set_in_cache
from .constants import _TMIO
from .errors import InvalidIDError, InvalidTrophyNumber, TMIOException

_log = logging.getLogger(__name__)

__all__ = ("PlayerTrophies", "TrophyLeaderboardPlayer")


class TrophyLeaderboardPlayer:
    """
    .. versionadded :: 0.4.0

    Represents a player on the trophy leaderboards

    Parameters
    ----------
    player_name : str
        The player's name
    club_tag : str | None
        The player's club tag
    player_id : str
        The player's ID
    rank : int
        The player's rank
    score : str
        The player's score
    zones : `list[PlayerZone]`
        The player's zones
    """

    def __init__(
        self,
        player_name: str,
        club_tag: str | None,
        player_id: str,
        rank: int,
        score: str,
        zones: list,
    ):
        self.player_name = player_name
        self.club_tag = club_tag
        self.player_id = player_id
        self.rank = rank
        self.score = score
        self.zones = zones

    @classmethod
    def _from_dict(cls: Self, raw: dict) -> Self:
        from .player import PlayerZone

        args = []
        player = raw.get("player")
        args.append(player.get("name"))
        args.append(_regex_it(player.get("tag", None)))
        args.append(player.get("id"))
        args.append(raw.get("rank"))
        args.append(_add_commas(int(raw.get("score"))))
        args.append(PlayerZone._parse_zones(player.get("zone"), [0, 0, 0, 0, 0]))

        return cls(*args)

    async def get_player(self: Self):
        """
        .. versionadded :: 0.4.0

        Gets the player object using the player ID.

        Returns
        -------
        :class:`Player`
            The player object
        """
        from .player import Player

        return await Player.get_player(self.player_id)


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
    trophies : :class:`list[int]`
        The number of trophies of the player.
    player_id : str | :class:`NoneType`, optional
        The Trackmania ID of the player
    """

    def __init__(
        self,
        echelon: int,
        last_change: datetime,
        points: int,
        trophies: list[int],
        player_id: str | None = None,
    ):
        """Constructor for the class."""
        self.echelon = echelon
        self._last_change = last_change
        self.points = points
        self.trophies = trophies
        self._player_id = player_id

    @classmethod
    def _from_dict(cls: Self, raw_trophy_data: dict, player_id: str) -> Self:
        """
        Creates a :class:`PlayerTrophies` object from the given dictionary.

        Parameters
        ----------
        raw_trophy_data : :class:`dict`
            The raw trophy data to parse.
        player_id : str
            The player ID to set.
        Returns
        -------
        :class:`PlayerTrophies`
            The parsed trophy data.
        """
        _log.debug("Creating a PlayerTrophies class from the given dictionary.")

        return cls(
            echelon=raw_trophy_data.get("echelon"),
            last_change=datetime.strptime(
                raw_trophy_data.get("timestamp"), "%Y-%m-%dT%H:%M:%S+00:00"
            ),
            points=raw_trophy_data.get("points"),
            trophies=raw_trophy_data.get("counts"),
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
        """
        .. versionadded :: 0.3.0

        Returns the total trophy score of the player.

        Returns
        -------
        int
            The total score.
        """

        score = (
            0
            + self.trophy(1) * 1
            + self.trophy(2) * 10
            + self.trophy(3) * 100
            + self.trophy(4) * 1_000
            + self.trophy(5) * 10_000
            + self.trophy(6) * 100_000
            + self.trophy(7) * 1_000_000
            + self.trophy(8) * 10_000_000
            + self.trophy(9) * 100_000_000
        )

        _log.debug(f"Score of {self.player_id} is {score}")

        return score

    def __str__(self) -> str:
        trophy_str = ""
        for i, trophyd in enumerate(self.trophies):
            trophy_str = trophy_str + f"T{i + 1} - " + _add_commas(trophyd) + "\n"

        trophy_str = trophy_str + f"\nTotal Trophies: {_add_commas(self.score())}"

        return trophy_str

    async def history(self, page: int = 0) -> dict:
        """
        .. versionadded :: 0.3.0

        Retrieves Trophy Gain and Loss history of a player.

        Parameters
        ----------
        page : int, optional
            page number of trophy history, by default 0
        Returns
        -------
        :class:`dict`
            Trophy history data.
        Raises
        ------
        InvalidIDError
            If an ID has not been set for the object.
        InvalidIDError
            If an invalid id has been set for the object.
        """
        _log.debug(
            f"Getting Trophy Leaderboard for Page: {page} and Player Id: {self.player_id}"
        )

        trophy_leaderboard_data = get_from_cache(f"trophy:{page}")
        if trophy_leaderboard_data is not None:
            return trophy_leaderboard_data.get("gains")

        api_client = _APIClient()

        if self.player_id is None:
            raise InvalidIDError("ID Has not been set for the Object")

        history = await api_client.get(
            _TMIO.build(
                [_TMIO.TABS.PLAYER, self.player_id, _TMIO.TABS.TROPHIES, str(page)]
            )
        )

        await api_client.close()

        with suppress(KeyError, TypeError):
            raise TMIOException(history["error"])

        set_in_cache(f"trophy:{page}", json.dumps(history), ex=3600)

        return history["gains"]

    @staticmethod
    async def top(page: int = 0) -> list[TrophyLeaderboardPlayer]:
        """
        .. versionadded :: 0.3.0

        Get's the top players ranked by trophies

        Parameters
        ----------
        page : int, optional
            The page of the leaderboards, by default 0

        Returns
        -------
        :class:`list[TrophyLeaderboardPlayer]`
            The players as a list of :class:`TrophyLeaderboardPlayer` objects.
        """
        _log.debug(f"Getting Page {page} of Trophy Leaderboards")

        trophy_leaderboard_data = get_from_cache(f"trophies:{page}")
        if trophy_leaderboard_data is not None:
            lb_players = []
            for top_player in trophy_leaderboard_data.get("ranks", []):
                lb_players.append(TrophyLeaderboardPlayer._from_dict(top_player))

        api_client = _APIClient()

        top_trophies = await api_client.get(
            _TMIO.build([_TMIO.TABS.TOP_TROPHIES, str(page)])
        )

        await api_client.close()

        with suppress(KeyError, TypeError):
            raise TMIOException(top_trophies["error"])

        set_in_cache(f"trophies:{page}", json.dumps(top_trophies), ex=3600)

        lb_players = []
        for top_player in top_trophies["ranks"]:
            lb_players.append(TrophyLeaderboardPlayer._from_dict(top_player))

        return lb_players
