from typing import List


class _BestData:
    """
    Data representing the best scores of the specific fields of a player.

    Parameters
    ----------
    best_rank : int
        The best rank of the player
    best_rank_time : str
        The best rank time of the player
    best_rank_div_rank : int
        The best rank in the division of the player
    best_div : int
        The best division of the player
    best_div_time : str
        The best division time of the player
    best_rank_in_div : int
        The best rank in the division of the player
    best_rank_in_div_time : str
        The best rank in the division time of the player
    best_rank_in_div_div : int
        The division where the `best_rank_in_div` was achieved.
    """

    def __init__(
        self,
        best_rank: int,
        best_rank_time: str,
        best_rank_div_rank: int,
        best_div: int,
        best_div_time: str,
        best_rank_in_div: int,
        best_rank_in_div_time: str,
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


class _COTDStats:
    """
    Represents the COTD stats of a player.

    best_primary : :class:`_BestData`
        The best primary stats of the player
    best_overall : :class:`_BestData`
        The best overall stats of the player
    total_wins : int
        The total wins of the player
    total_div_wins : int
        The total wins in the division of the player
    avg_rank : float
        The average rank of the player
    avg_div_rank : float
        The average rank in the division of the player
    avg_div : float
        The average division of the player
    win_streak : int
        The win streak of the player
    div_win_streak: int
        The division win streak of the player.
    """

    def __init__(
        self,
        best_primary: _BestData,
        best_overall: _BestData,
        total_wins: int,
        total_div_wins: int,
        avg_rank: float,
        avg_div_rank: float,
        avg_div: float,
        win_streak: int,
        div_win_streak: int,
    ):
        self.best_primary = best_primary
        self.best_overall = best_overall
        self.total_wins = total_wins
        self.total_div_wins = total_div_wins
        self.avg_rank = avg_rank
        self.avg_div_rank = avg_div_rank
        self.avg_div = avg_div
        self.win_streak = win_streak
        self.div_win_streak = div_win_streak


class COTD:
    """
    Represents a single COTD result of a player.

    cotd_id : int
        The COTD ID.
    timestamp : str
        The timestamp of the COTD
    name : str
        The name of the COTD
    div : int
        The division of the player
    rank : int
        The rank of the player
    div_rank : int
        The division ranking of the player
    score : int
        The score of the player
    total_players : int
        The total players playing the COTD
    rerun : bool
        Whether the COTD is a rerun or not
    """

    def __init__(
        self,
        cotd_id: int,
        timestamp: str,
        name: str,
        div: int,
        rank: int,
        div_rank: int,
        score: int,
        total_players: int,
    ):
        self.cotd_id = cotd_id
        self.timestamp = timestamp
        self.name = name
        self.div = div
        self.rank = rank
        self.div_rank = div_rank
        self.score = score
        self.total_players = total_players

        self.rerun = (
            True if self.name.endswith("#2") or self.name.endswith("#3") else False
        )


class PlayerCOTD:
    """
    Represents a player's COTD stats.

    Parameters
    ----------
    stats : :class:`_COTDStats`
        The stats of the player
    cotds : :class:`List[COTD]`
        The COTDs of the player
    """

    def __init__(self, stats: _COTDStats, cotds: List[COTD]):
        self.stats = stats
        self.cotds = cotds
