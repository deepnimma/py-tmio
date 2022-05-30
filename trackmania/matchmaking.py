import logging
from contextlib import suppress
from datetime import datetime

from typing_extensions import Self

from ._util import _frmt_str_to_datetime, _regex_it
from .api import _APIClient
from .base import MatchmakingObject
from .config import get_from_cache, set_in_cache
from .constants import _TMIO
from .errors import InvalidIDError, TMIOException

_log = logging.getLogger(__name__)

__all__ = (
    "MatchmakingLeaderboardPlayer",
    "PlayerMatchmakingResult",
    "PlayerMatchmaking",
)


async def _get_history(player_id: str, type_id: int, page: int) -> list[dict]:
    if player_id is None:
        raise InvalidIDError("Player ID is not set.")

    _log.debug("Getting matchmaking history for player %s and page %d", player_id, page)

    matchmaking_history = get_from_cache(
        f"matchmaking_history:{page}:{type_id}:{player_id}"
    )
    if matchmaking_history is not None:
        return matchmaking_history.get("history")

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

    set_in_cache(
        f"matchmaking_history:{page}:{type_id}:{player_id}", match_history, ex=3600
    )

    return match_history.get("history", [])


class MatchmakingLeaderboardPlayer(MatchmakingObject):
    """
    Represents a player on the Matchmaking leaderboards.

    Parameters
    ----------
    player_name : str
        The name of the player.
    player_tag : str | None
        The tag of the player.
    player_id : str
        The ID of the player.
    rank : int
        The rank of the player.
    score : int
        The score of the player.
    progression : int
        The progression of the player.
    """

    def __init__(
        self,
        player_name: str,
        player_tag: str | None,
        player_id: str,
        rank: int,
        score: int,
        progression: int,
        division: int,
    ):
        self.player_name = player_name
        self.player_tag = player_tag
        self.player_id = player_id
        self.rank = rank
        self.score = score
        self.progression = progression
        self.division = division

    @classmethod
    def _from_dict(cls: Self, raw_data: dict) -> Self:
        player_name = raw_data["player"].get("name")
        player_tag = _regex_it(raw_data["player"].get("tag", None))
        player_id = raw_data["player"].get("id")
        rank = raw_data.get("rank")
        score = raw_data.get("score")
        progression = raw_data.get("progression")
        division = raw_data.get("division")

        args = [
            player_name,
            player_tag,
            player_id,
            rank,
            score,
            progression,
            division,
        ]

        return cls(*args)

    async def player(self: Self):
        """
        Returns the player who owns this position on the leaderboard.

        Returns
        -------
        :class:`Player`
            The player.
        """
        from .player import Player

        return await Player.get_player(self.player_id)


async def _get_top_matchmaking(
    page: int = 0, royal: bool = False
) -> list[MatchmakingLeaderboardPlayer]:
    _log.debug(f"Getting top matchmaking players page {page}. Royal? {royal}")
    tops = []

    top_matchmaking_data = get_from_cache(f"top_matchmaking:{page}:{royal}")
    if top_matchmaking_data is not None:
        for pos in top_matchmaking_data.get("ranks", []):
            tops.append(MatchmakingLeaderboardPlayer._from_dict(pos))

        return tops

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

    set_in_cache(f"top_matchmaking:{page}:{royal}", match_history, ex=3600)

    for pos in match_history.get("ranks", []):
        tops.append(MatchmakingLeaderboardPlayer._from_dict(pos))

    return tops


class PlayerMatchmakingResult(MatchmakingObject):
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
    def _from_dict(cls, data: dict, player_id: str = None) -> Self:
        _log.debug("Creating a PlayerMatchmakingResult class from given dictionary")

        after_score = data.get("afterscore")
        leave = data.get("leave")
        live_id = data.get("lid")
        mvp = data.get("mvp")
        start_time = _frmt_str_to_datetime(data.get("startime"))
        win = data.get("win")

        args = [after_score, leave, live_id, mvp, player_id, start_time, win]

        return cls(*args)


class PlayerMatchmaking(MatchmakingObject):
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
    def _from_dict(mm_data: dict, player_id: str = None) -> Self:
        """
        Parses the matchmaking data of the player and returns 2 :class:`PlayerMatchmaking` objects.
            One for 3v3 Matchmaking and the other for Royal matchmaking.

        Parameters
        ----------
        mm_data : :class:`list[dict]`
            The matchmaking data.
        player_id : str, optional
            The player's ID. Defaults to None
        Returns
        -------
        :class:`list[PlayerMatchmaking]`
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
    def __parse_3v3(cls, data: dict, player_id: str = None) -> Self:
        """
        Parses matchmaking data for 3v3 and royal type matchmaking.

        Parameters
        ----------
        data : :class:`dict`
            The matchmaking data only.
        Returns
        -------
        :class:`PlayerMatchmaking`
            The parsed data.
        """
        _log.debug(
            f"Parsing Data from dictionary for PlayerMatchmaking class. ID supplied: {player_id}"
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

    def __str__(self) -> str:
        progression = self.progression
        progress = self.progress
        rank = self.rank
        score = self.score
        division = self.division
        division_str = self.division_str
        max_points = self.max_points

        return f"Progression: {progression}\nProgress: {progress}\nRank: {rank}\nScore: {score}\nDivision: {division_str} - {division}\n\nPoints to Next Division: {max_points + 1}"

    async def history(self, page: int = 0) -> list[PlayerMatchmakingResult]:
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
        :class:`list[PlayerMatchmakingResult]`
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
    async def top_matchmaking(
        page: int = 0, royal: bool = False
    ) -> list[MatchmakingLeaderboardPlayer]:
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
        :class:`list[MatchmakingLeaderboardPlayer]`
            The top matchmaking players by score. Each page contains 50 players.
        """
        return await _get_top_matchmaking(page, royal)
