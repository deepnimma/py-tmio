import json
import logging
from contextlib import suppress
from datetime import datetime
from types import NoneType
from typing import Dict, List

import redis

from trackmania.errors import TMIOException

from .api import _APIClient
from .config import Client
from .constants import _TMIO
from .errors import InvalidIDError, TMIOException

_log = logging.getLogger(__name__)

__all__ = (
    "BestCOTDStats",
    "PlayerCOTDStats",
    "PlayerCOTDResults",
    "PlayerCOTD",
    "COTD",
)


class BestCOTDStats:
    """
    .. versionadded :: 0.3.0

    Parameters
    ----------
    best_rank : int
        The best rank achieved by the player.
    best_rank_time : int
        The time when `best_rank` was achieved.
    best_rank_div_rank : int
        The rank achieved in the division of the `best_rank`.
    best_div : int
        The best division of the player.
    best_div_time : int
        The time when `best_div` was achieved.
    best_rank_in_div : int
        The best rank the player achieved in any division.
    best_rank_in_div_time : int
        The time when `best_rank_in_div` was achieved.
    best_rank_in_div_div : int
        The division of the `best_rank_in_div`.
    """

    def __init__(
        self,
        best_rank: int,
        best_rank_time: datetime,
        best_rank_div_rank: int,
        best_div: int,
        best_div_time: datetime,
        best_rank_in_div: int,
        best_rank_in_div_time: datetime,
        best_rank_in_div_div: int,
    ):
        self.best_rank = best_rank
        self.best_rank_time = best_rank_time
        self.best_rank_div_rank = best_rank_div_rank
        self.best_div = best_div
        self.best_div_time = best_div_time
        self.best_rank_in_div = best_rank_in_div
        self.best_rank_in_div_time = best_rank_in_div_time
        self.best_rank_in_div_div = best_rank_in_div_div

    @classmethod
    def _from_dict(cls, raw: Dict):
        _log.debug("Creating a BestCOTDStats class from given dictionary")

        best_rank = raw["bestrank"]
        best_rank_time = datetime.strptime(
            raw["bestranktime"], "%Y-%m-%dT%H:%M:%S+00:00"
        )
        best_rank_div_rank = raw["bestrankdivrank"]
        best_div = raw["bestdiv"]
        best_div_time = datetime.strptime(raw["bestdivtime"], "%Y-%m-%dT%H:%M:%S+00:00")
        best_rank_in_div = raw["bestrankindiv"]
        best_rank_in_div_time = datetime.strptime(
            raw["bestrankindivtime"], "%Y-%m-%dT%H:%M:%S+00:00"
        )
        best_rank_in_div_div = raw["bestrankindivdiv"]

        return cls(
            best_rank,
            best_rank_time,
            best_rank_div_rank,
            best_div,
            best_div_time,
            best_rank_in_div,
            best_rank_in_div_time,
            best_rank_in_div_div,
        )


class PlayerCOTDStats:
    """
    .. versionadded :: 0.3.0

    Parameters
    ----------
    average_div : int
        The average div of the player
    average_div_rank : int
        The average div rank of the player
    average_rank : int
        The average rank of the player
    best_overall : int
        The best overall rank of the player
    best_primary : int
        The best primary rank of the player
    div_win_streak : int
        The div win streak of the player
    total_div_wins : int
        The total div wins of the player
    total_wins : int
        The total wins of the player
    win_streak : int
        The win streak of the player
    """

    def __init__(
        self,
        average_div: float,
        average_div_rank: float,
        average_rank: float,
        best_overall: BestCOTDStats,
        best_primary: BestCOTDStats,
        div_win_streak: int,
        total_div_wins: int,
        total_wins: int,
        win_streak: int,
    ):
        self.average_div = average_div
        self.average_div_rank = average_div_rank
        self.average_rank = average_rank
        self.best_overall = best_overall
        self.best_primary = best_primary
        self.div_win_streak = div_win_streak
        self.total_div_wins = total_div_wins
        self.total_wins = total_wins
        self.win_streak = win_streak

    @classmethod
    def _from_dict(cls, raw: Dict):
        _log.debug("Creating a PlayerCOTDStats class from given dictionary")

        average_div = raw["avgdiv"]
        average_div_rank = raw["avgdivrank"]
        average_rank = raw["avgrank"]
        best_overall = BestCOTDStats._from_dict(raw["bestoverall"])
        best_primary = BestCOTDStats._from_dict(raw["bestprimary"])
        div_win_streak = raw["divwinstreak"]
        total_div_wins = raw["totaldivwins"]
        total_wins = raw["totalwins"]
        win_streak = raw["winstreak"]

        return cls(
            average_div,
            average_div_rank,
            average_rank,
            best_overall,
            best_primary,
            div_win_streak,
            total_div_wins,
            total_wins,
            win_streak,
        )


class PlayerCOTDResults:
    """
    .. versionadded :: 0.3.0

    Represents a Player's COTD Result.

    Parameters
    ----------
    id : int
        The ID of the COTD.
    timestamp : :class:`datetime`
        The timestamp of the COTD.
    name : str
        The name of the COTD
    div : int
        The division the player achieved
    rank : int
        The rank the player achieved
    div_rank : int | None
        The rank the player achieved in the division. If the player did not play in the division, this will be ``None``.
    score : int | None
        The score of the player. If the player did not play after qualifying for the COTD, this will be ``None``.
    total_players : int
        The total players that played this COTD.
    """

    def __init__(
        self,
        id: int,
        timestamp: datetime,
        name: str,
        div: int,
        rank: int,
        div_rank: int | None,
        score: int | None,
        total_players: int,
    ):
        self.id = id
        self.timestamp = timestamp
        self.name = name
        self.div = div
        self.rank = rank
        self.div_rank = div_rank
        self.score = score
        self.total_players = total_players

    @classmethod
    def _from_dict(cls, raw: Dict):
        _log.debug("Creating a PlayerCOTDResults class from given dictionary")

        id = raw["id"]
        timestamp = datetime.strptime(raw["timestamp"], "%Y-%m-%dT%H:%M:%S+00:00")
        name = raw["name"]
        div = raw["div"]
        rank = raw["rank"]
        div_rank = raw["divrank"] if raw["divrank"] != 0 else None
        score = raw["score"] if raw["score"] != 0 else None
        total_players = raw["totalplayers"]

        return cls(
            id,
            timestamp,
            name,
            div,
            rank,
            div_rank,
            score,
            total_players,
        )


class PlayerCOTD:
    """
    .. versionadded :: 0.3.0

    The Player's COTD Data

    Parameters
    ----------
    total : int
        Total COTD's Played
    recent_results : :class:`List[PlayerCOTDResults]`
        Represents the recent COTD results the player has gotten
    stats : :class:`PlayerCOTDStats`
        Represents the Statistics of the Player's COTD career
    player_id : str
        The player's ID
    """

    def __init__(
        self,
        total: int,
        recent_results: List[PlayerCOTDResults],
        stats: PlayerCOTDStats,
        player_id: str,
    ):
        self.total = total
        self.recent_results = recent_results
        self.stats = stats
        self.player_id = player_id

    @classmethod
    def _from_dict(cls, page_data: Dict, player_id: str):
        _log.debug("Creating a PlayerCOTD class from given dictionary")

        total = page_data["total"]
        stats = PlayerCOTDStats._from_dict(page_data["stats"])
        player_id = player_id

        recent_results = []
        for cotd in page_data["cotds"]:
            recent_results.append(PlayerCOTDResults._from_dict(cotd))

        return cls(
            total,
            recent_results,
            stats,
            player_id,
        )

    @staticmethod
    async def get_page(player_id: str, page: int = 0):
        """
        .. versionadded :: 0.3.0

        Gets the Player's COTD Stats of a particular page.

        Parameters
        ----------
        player_id : str
            The player's ID
        page : int, optional
            The page of the ID, by default 0
        """
        _log.debug(f"Getting COTD Stats for Player {player_id} and page {page}")

        cache_client = Client._get_cache_client()

        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            if cache_client.exists(f"playercotd:{player_id}:{page}"):
                _log.debug(
                    f"Player {player_id}'s page {page} cotd results found in cache"
                )
                return PlayerCOTD._from_dict(
                    json.loads(
                        cache_client.get(f"playercotd:{player_id}:{page}").decode(
                            "utf-8"
                        )
                    ),
                    player_id,
                )

        api_client = _APIClient()
        page_data = await api_client.get(
            _TMIO.build([_TMIO.TABS.PLAYER, player_id, _TMIO.TABS.COTD, str(page)])
        )
        await api_client.close()

        with suppress(KeyError, TypeError):
            raise TMIOException(page_data["error"])
        if isinstance(page_data, NoneType):
            raise InvalidIDError("Invalid PlayerID Given")
        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            _log.debug(f"Caching Player {player_id} Page {page}")
            cache_client.set(f"playercotd:{player_id}:{page}", json.dumps(page_data))

        return PlayerCOTD._from_dict(page_data, player_id)


class COTD:
    """
    .. versionadded :: 0.3.0

    Represents a Cup of the Day

    Parameters
    ----------
    cotd_id : int
        The cotd id
    name : str
        The name of the cotd
    player_count : int
        The number of players that played the :class:`COTD`
    start_date : :class:`datetime`
        The start date of the COTD
    end_date : :class:`datetime`
        The end date of the COTD
    """

    def __init__(
        self,
        cotd_id: int,
        name: str,
        player_count: int,
        start_date: datetime,
        end_date: datetime,
    ):
        self.cotd_id = cotd_id
        self.name = name
        self.player_count = player_count
        self.start_date = start_date
        self.end_date = end_date

    @classmethod
    def _from_dict(cls, raw: Dict):
        _log.debug("Creating a COTD class from given dictionary")

        cotd_id = raw["id"]
        name = raw["name"]
        player_count = raw["players"]
        start_date = datetime.utcfromtimestamp(raw["starttime"])
        end_date = datetime.utcfromtimestamp(raw["endtime"])

        return cls(
            cotd_id,
            name,
            player_count,
            start_date,
            end_date,
        )

    @staticmethod
    async def get(page: int = 0) -> List:
        """
        .. versionadded :: 0.3.0

        Fetches the Latest COTDs and returns its data.

        Parameters
        ----------
        page : int, optional
            The page, each page contains 12 items. by default 0

        Returns
        -------
        :class:`List[COTD]`
            The COTDs
        """
        _log.debug(f"Getting COTD Page {page}")

        cache_client = Client._get_cache_client()

        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            if cache_client.exists(f"cotd:{page}"):
                _log.debug(f"COTD Page {page} found in cache")
                cotds = json.loads(cache_client.get(f"cotd:{page}").decode("utf-8"))

                acotds = []
                for cotd in cotds["competitions"]:
                    acotds.append(COTD._from_dict(cotd))

                return acotds

        api_client = _APIClient()
        all_cotds = await api_client.get(_TMIO.build([_TMIO.TABS.COTD, page]))
        await api_client.close()

        with suppress(KeyError, TypeError):
            raise TMIOException(all_cotds["error"])
        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            _log.debug(f"Caching COTD Page {page}")
            cache_client.set(f"cotd:{page}", json.dumps(all_cotds), ex=7200)

        acotds = []
        for cotd in all_cotds["competitions"]:
            acotds.append(COTD._from_dict(cotd))

        return acotds
