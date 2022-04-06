import json
import logging
from contextlib import suppress
from datetime import datetime
from typing import Dict, List

import redis

from trackmania.errors import TMIOException

from .api import _APIClient
from .config import Client
from .constants import TMIO
from .player import Player

_log = logging.getLogger(__name__)


class BestCOTDStats:
    """
    .. versionadded :: 0.3.0

    Parameters
    ----------
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
        best_rank = raw["bestrank"]
        best_rank_time = datetime.strptime(
            raw["bestranktime"], "%Y-%m-%dT%H:%M:%S+00:00"
        )
        best_rank_div_rank = raw["bestrankdivtime"]
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
