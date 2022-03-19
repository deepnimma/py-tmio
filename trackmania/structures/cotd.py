from typing import List


class _BestData:
    """Data representing the best scores of the specific fields of a player.

    :param best_rank: The best rank of the player.
    :type best_rank: int
    :param best_rank_time: The time of the best rank of the player.
    :type best_rank_time: str
    :param best_rank_div_rank: The best rank of the player in the
            division.
    :type best_rank_div_rank: int
    :param best_div: The best division of the player.
    :type best_div: int
    :param best_div_time: The time of the best division of the
            player.
    :type best_div_time: str
    :param best_rank_in_div: The best rank of the player in the
            division.
    :type best_rank_in_div: int
    :param best_rank_in_div_time: The time of the best rank of the
            player in the division.
    :type best_rank_in_div_time: str
    :param best_rank_in_div_div: The division of the player best rank
            in division.
    :type best_rank_in_div_div: int

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
    """Represents the COTD stats of a player.

    :param best_primary: The best primary stats of the player.
    :type best_primary: _BestData
    :param best_overall: The best overall stats of the player.
    :type best_overall: _BestData
    :param total_wins: The total wins of the player.
    :type total_wins: int
    :param total_div_wins: The total wins of the player in the
            division.
    :type total_div_wins: int
    :param avg_rank: The average rank of the player.
    :type avg_rank: float
    :param avg_div_rank: The average rank of the player in the
            division.
    :type avg_div_rank: float
    :param avg_div: The average division of the player.
    :type avg_div: float
    :param win_streak: The win streak of the player.
    :type win_streak: int

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
    """Represents a single COTD result of a player.

    :param cotd_id: The COTD ID.
    :type cotd_id: int
    :param timestamp: The timestamp of the COTD.
    :type timestamp: str
    :param name: The name of the COTD.
    :type name: str
    :param div: The division of the player.
    :type div: int
    :param rank: The rank of the player.
    :type rank: int
    :param div_rank: The rank of the player in the division.
    :type div_rank: int
    :param score: The score of the player.
    :type score: int
    :param total_players: The total players playing the COTD.
    :type total_players: int
    :param rerun: Whether the COTD is a rerun.
    :type rerun: bool

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
    """ """

    def __init__(self, stats: _COTDStats, cotds: List[COTD]):
        self.stats = stats
        self.cotds = cotds
