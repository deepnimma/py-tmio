import json
import logging
from contextlib import suppress
from datetime import datetime
from typing import Dict, List

import redis

from .api import APIClient
from .config import Client
from .constants import TMIO
from .errors import InvalidIDError, TMIOException

_log = logging.getLogger(__name__)


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
    player_id : str
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
        after_score = data["afterscore"]
        leave = data["leave"]
        live_id = data["lid"]
        mvp = data["mvp"]
        start_time = datetime.strptime(data["starttime"], "%Y-%m-%dT%H:%M:%SZ")
        win = data["win"]

        return cls(after_score, leave, live_id, mvp, player_id, start_time, win)


class PlayerMatchmaking:
    """
    .. versionadded :: 0.1.0

    Class that represents the player matchmaking details

    Parameters
    ----------
    type : str
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
    min_points : ints: int
        The points required to reach the current division.
    max_points : ints: int
        The points required to move up the rank.
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
        player_id: str = None,
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
        self.division_str = MATCHMAKING_STRING[division]
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
        matchmaking_data = list()

        if len(mm_data) == 0:
            matchmaking_data.extend([None, None])
        elif len(mm_data) == 1:
            matchmaking_data.extend(
                [PlayerMatchmaking.__parse_3v3(mm_data[0], player_id), None]
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
        if "info" in data:
            typename = data["info"]["typename"]
            typeid = data["info"]["typeid"]
            progression = data["info"]["progression"]
            rank = data["info"]["rank"]
            score = data["info"]["score"]
            division = data["info"]["division"]["position"]
            min_points = data["info"]["division"]["minpoints"]
            max_points = data["info"]["division"]["maxpoints"]
        else:
            typename = data["typename"]
            typeid = data["typeid"]
            progression = data["progression"]
            rank = data["rank"]
            score = data["score"]
            division = data["division"]["position"]
            min_points = data["division"]["minpoints"]
            max_points = data["division"]["maxpoints"]

        return cls(
            typename,
            typeid,
            progression,
            rank,
            score,
            division,
            min_points,
            max_points,
            player_id,
        )

    @property
    def min_points(self):
        """min points property"""
        return self._min_points

    @property
    def max_points(self):
        """max points property"""
        return self._max_points

    async def history(self, page: int = 0) -> List[PlayerMatchmakingResult]:
        """
        .. versionadded :: 0.3.0

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
        if self.player_id is None:
            raise InvalidIDError("Player ID is not set")

        _log.debug(
            f"Getting matchmaking history page {page} for player {self.player_id}"
        )

        cache_client = redis.Redis(
            host=Client.REDIS_HOST,
            port=Client.REDIS_PORT,
            db=Client.REDIS_DB,
            password=Client.REDIS_PASSWORD,
        )

        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            if cache_client.exists(
                f"mm_history:{page}:{self.type_id}:{self.player_id}"
            ):
                _log.debug(f"Found matchmaking history for page {page} in cache")

                player_results = list()
                history = json.loads(
                    cache_client.get(
                        f"mm_history:{page}:{self.type_id}:{self.player_id}"
                    ).decode("utf-8")
                )

                for item in history["matches"]:
                    player_results.append(PlayerMatchmakingResult._from_dict(item))

                return player_results

        api_client = APIClient()
        match_history = await api_client.get(
            TMIO.build(
                [
                    TMIO.TABS.PLAYER,
                    self.player_id,
                    TMIO.TABS.MATCHES,
                    self.type_id,
                    str(page),
                ]
            )
        )
        await api_client.close()

        with suppress(KeyError, TypeError):
            _log.error("This is a trackmania.io error")
            raise TMIOException(match_history["error"])
        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            _log.debug(f"Saving matchmaking history for page {page} to cache")
            cache_client.set(
                f"mm_history:{page}:{self.type_id}:{self.player_id}",
                json.dumps(match_history),
                ex=3600,
            )

        player_results = list()
        for match in match_history["matches"]:
            player_results.append(PlayerMatchmakingResult._from_dict(match))

        return player_results

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
        _log.debug(f"Getting top matchmaking players page {page}. Royal? {royal}")

        cache_client = redis.Redis(
            host=Client.REDIS_HOST,
            port=Client.REDIS_PORT,
            db=Client.REDIS_DB,
            password=Client.REDIS_PASSWORD,
        )

        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            if cache_client.exists(f"top_matchmaking:{page}:{royal}"):
                _log.debug(f"Found top matchmaking players for page {page} in cache")
                return json.loads(
                    cache_client.get(f"top_matchmaking:{page}:{royal}").decode("utf-8")
                )["ranks"]
        api_client = APIClient()

        if not royal:
            match_history = await api_client.get(
                TMIO.build([TMIO.TABS.TOP_MATCHMAKING, str(page)])
            )
        else:
            match_history = await api_client.get(
                TMIO.build([TMIO.TABS.TOP_ROYAL, str(page)])
            )

        await api_client.close()

        with suppress(KeyError, TypeError):
            _log.error("This is a trackmania.io error")
            raise TMIOException(match_history["error"])
        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            _log.debug(f"Caching top matchmaking players for page {page}")
            cache_client.set(
                f"top_matchmaking:{page}:{royal}", json.dumps(match_history), ex=3600
            )

        return match_history["ranks"]
