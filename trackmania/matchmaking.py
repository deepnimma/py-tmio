import json
import logging
from contextlib import suppress
from datetime import datetime
from typing import Dict, List

import redis

from .api import _APIClient
from .config import Client
from .constants import _TMIO
from .errors import InvalidIDError, TMIOException

_log = logging.getLogger(__name__)

__all__ = (
    "PlayerMatchmakingResult",
    "PlayerMatchmaking",
)


async def _get_top_matchmaking(page: int = 0, royal: bool = False):
    _log.debug(f"Getting top matchmaking players page {page}. Royal? {royal}")

    cache_client = Client._get_cache_client()

    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        if cache_client.exists(f"top_matchmaking:{page}:{royal}"):
            _log.debug(f"Found top matchmaking players for page {page} in cache")
            return json.loads(
                cache_client.get(f"top_matchmaking:{page}:{royal}").decode("utf-8")
            ).get("ranks")
    api_client = _APIClient()

    if not royal:
        match_history = await api_client.get(
            _TMIO.build([_TMIO.TABS.TOP_MATCHMAKING, str(page)])
        )
    else:
        match_history = await api_client.get(
            _TMIO.build([_TMIO.TABS.TOP_ROYAL, str(page)])
        )

    await api_client.close()

    with suppress(KeyError, TypeError):
        raise TMIOException(match_history["error"])
    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        _log.debug(f"Caching top matchmaking players for page {page}")
        cache_client.set(
            f"top_matchmaking:{page}:{royal}", json.dumps(match_history), ex=3600
        )

    return match_history.get("ranks")


async def _get_history(player_id: str, type_id: int, page: int) -> List[Dict]:
    if player_id is None:
        raise InvalidIDError("Player ID is not set.")

    _log.debug("Getting matchmaking history for player %s and page %d", player_id, page)

    cache_client = Client._get_cache_client()

    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        if cache_client.exists(f"mm_hist:{page}:{type_id}:{player_id}"):
            _log.debug("Found matchmaking history for page %s in cache", page)
            return json.loads(
                cache_client.get(f"mm_hist:{page}:{type_id}:{player_id}").decode(
                    "utf-8"
                )
            )["history"]

    api_client = _APIClient()
    match_history = await api_client.get(
        _TMIO.build(
            [
                _TMIO.TABS.PLAYER,
                player_id,
                _TMIO.TABS.MATCHES,
                type_id,
                page,
            ]
        )
    )
    await api_client.close()

    with suppress(KeyError, TypeError):
        raise TMIOException(match_history["error"])
    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        _log.debug(f"Saving matchmaking history for page {page} to cache")
        cache_client.set(
            f"mm_history:{page}:{type_id}:{player_id}",
            json.dumps(match_history),
            ex=3600,
        )

    return match_history.get("history", [])


class PlayerMatchmakingResult:
    """
    .. versionadded :: 0.3.0

    Represent's a player's matchmaking result

    Parameters
    ----------
    after_score : int
        The player's matchmaking score after the match
    leave : bool
        Whether the player left the match
    live_id : str
        The live id of the match
    mvp : bool
        Whether the player was the mvp of the match
    player_id : str | None
        The player's ID
    start_time : :class:`datetime`
        The date the match started
    win : bool
        Whether the player won the match
    """

    def __init__(
        self,
        after_score: int,
        leave: bool,
        live_id: str,
        mvp: bool,
        player_id: str | None,
        start_time: datetime,
        win: bool,
    ):
        self.after_score = after_score
        self.leave = leave
        self.live_id = live_id
        self.mvp = mvp
        self.player_id = player_id
        self.start_time = start_time
        self.win = win

    @classmethod
    def _from_dict(cls, data: Dict, player_id: str = None):
        _log.debug("Creating a PlayerMatchmakingResult class from given dictionary")

        after_score = data.get("afterscore")
        leave = data.get("leave")
        live_id = data.get("lid")
        mvp = data.get("mvp")
        start_time = datetime.strptime(data.get("startime"), "%Y-%m-%dT%H:%M:%SZ")
        win = data.get("win")

        args = [after_score, leave, live_id, mvp, player_id, start_time, win]

        return cls(*args)


class PlayerMatchmaking:
    """
    .. versionadded :: 0.1.0

    Class that represents the player matchmaking details

    Parameters
    ----------
    matchmaking_type : str
        The type of matchmaking, either "3v3" or "Royal"
    type_id : int
        The type of matchmaking as 0 or 1, 0 for "3v3" and 1 for "Royal"
    progression : int
        The progression of the player's score in matchmaking
    rank : int
        The rank of the player in matchmaking
    score : int
        The score of the player in matchmaking
    division : int
        The division of the player in matchmaking
    division_str : str: str
        The division of the player in matchmaking as a string
    min_points : int
        The points required to reach the current division.
    max_points : int
        The points required to move up the rank.
    player_id : str | None
        The player's ID. Defaults to None
    """

    def __init__(
        self,
        matchmaking_type: str,
        type_id: int,
        progression: int,
        rank: int,
        score: int,
        division: int,
        min_points: int,
        max_points: int,
        player_id: str | None = None,
    ):
        """Constructor for the class."""
        MATCHMAKING_STRING = {
            1: "Bronze 3",
            2: "Bronze 2",
            3: "Bronze 1",
            4: "Silver 3",
            5: "Silver 2",
            6: "Silver 1",
            7: "Gold 3",
            8: "Gold 2",
            9: "Gold 1",
            10: "Master 3",
            11: "Master 2",
            12: "Master 1",
            13: "Trackmaster",
        }

        self.matchmaking_type = matchmaking_type
        self.type_id = type_id
        self.rank = rank
        self.score = score
        self.progression = progression
        self.division = division
        self.division_str = MATCHMAKING_STRING.get(division)
        self._min_points = min_points
        self._max_points = 1 if max_points == 0 else max_points
        self.player_id = player_id

        try:
            self.progress = round(
                (score - min_points) / (max_points - min_points) * 100, 2
            )
        except ZeroDivisionError:
            self.progress = 0

    @staticmethod
    def _from_dict(mm_data: Dict, player_id: str = None):
        """
        Parses the matchmaking data of the player and returns 2 :class:`PlayerMatchmaking` objects.
            One for 3v3 Matchmaking and the other for Royal matchmaking.

        Parameters
        ----------
        mm_data : :class:`List[Dict]`
            The matchmaking data.
        player_id : str, optional
            The player's ID. Defaults to None
        Returns
        -------
        :class:`List[PlayerMatchmaking]`
            The list of matchmaking data, one for 3v3 and other other one for royal.
        """
        _log.debug("Creating a PlayerMatchmaking class from given dictionary")

        matchmaking_data = []

        if len(mm_data) == 0:
            matchmaking_data.extend([None, None])
        elif len(mm_data) == 1:
            mm_obj = PlayerMatchmaking.__parse_3v3(mm_data[0])
            matchmaking_data.extend(
                [mm_obj, None] if mm_obj.type_id == 2 else [None, mm_obj]
            )
        else:
            matchmaking_data.extend(
                [
                    PlayerMatchmaking.__parse_3v3(mm_data[0], player_id),
                    PlayerMatchmaking.__parse_3v3(mm_data[1], player_id),
                ]
            )

        return matchmaking_data

    @classmethod
    def __parse_3v3(cls, data: Dict, player_id: str = None):
        """
        Parses matchmaking data for 3v3 and royal type matchmaking.

        Parameters
        ----------
        data : :class:`Dict`
            The matchmaking data only.
        Returns
        -------
        :class:`PlayerMatchmaking`
            The parsed data.
        """
        _log.debug(
            f"Parsing Data from Dictionary for PlayerMatchmaking class. ID supplied: {player_id}"
        )

        if "info" in data:
            data = data.get("info")

        type_name = data.get("typename")
        type_id = data.get("typeid")
        progression = data.get("progression")
        rank = data.get("rank")
        score = data.get("score")
        division = data.get("division").get("position")
        min_points = data.get("division").get("minpoints")
        max_points = data.get("division").get("maxpoints")

        args = [
            type_name,
            type_id,
            progression,
            rank,
            score,
            division,
            min_points,
            max_points,
            player_id,
        ]

        return cls(*args)

    @property
    def min_points(self):
        """min points"""
        return self._min_points

    @property
    def max_points(self):
        """max points"""
        return self._max_points

    def __str__(self):
        progression = self.progression
        progress = self.progress
        rank = self.rank
        score = self.score
        division = self.division
        division_str = self.division_str
        max_points = self.max_points

        return f"Progression: {progression}\nProgress: {progress}\nRank: {rank}\nScore: {score}\nDivision: {division_str} - {division}\n\nPoints to Next Division: {max_points + 1}"

    async def history(self, page: int = 0) -> List[PlayerMatchmakingResult]:
        """
        .. versionadded :: 0.3.0
        .. versionchanged :: 0.4.0
            Use `_get_history()` helper command.

        History of recent matches in this matchmaking

        Parameters
        ----------
        page : int, optional
            The page number, by default 0

        Returns
        -------
        :class:`List[PlayerMatchmakingResult]`
            The list of matchmaking results

        Raises
        ------
        :class:`InvalidIDError`
            If the player_id is not set.
        """
        matches = await _get_history(self.player_id, self.type_id, page)

        match_results = []
        for match in matches:
            match_results.append(
                PlayerMatchmakingResult._from_dict(match), self.player_id
            )

        return match_results

    @staticmethod
    async def top_matchmaking(page: int = 0, royal: bool = False) -> List[Dict]:
        """
        .. versionadded :: 0.3.0

        Top matchmaking players

        Parameters
        ----------
        page : int, optional
            The page number, by default 0
        royal : bool, optional
            Whether to get the top matchmaking players for royal, by default False

        Returns
        -------
        :class:`List[Dict]`
            The top matchmaking players by score. Each page contains 50 players.
        """
        return await _get_top_matchmaking(page, royal)
