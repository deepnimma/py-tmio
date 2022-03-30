from typing import Dict, List

from .medal_times import MedalTimes

__all__ = ("TOTD",)


# pylint: disable=too-many-arguments, too-many-instance-attributes, too-few-public-methods
class TOTD:
    """
    Class that represents a totd map

    Parameters
    ----------
    campaign_id : int
        The campaign id of the map
    map_author_id : str
        The id of the author of the map
    map_name : str
        The name of the map
    map_type : str
        The type of the map
    medal_times : :class:`MedalTimes`
        The medal times of the map
    map_id : str
        The id of the map
    map_uid : str
        The uid of the map
    timestamp : str
        The timestamp of the map
    file_url : str
        The url of the map file
    thumbnail_url : str
        The url of the map thumbnail
    week_day : int
        The week day of the map
    month_day : int
        The month day of the map
    leaderboard_uid : str
        The uid of the leaderboard
    leaderboard : :class:`List[Dict]` | None
        The leaderboard of the map. Defaults to None
    """

    def __init__(
        self,
        campaign_id: int,
        map_author_id: str,
        map_name: str,
        map_type: str,
        medal_times: MedalTimes,
        map_id: str,
        map_uid: str,
        timestamp: str,
        file_url: str,
        thumbnail_url: str,
        week_day: int,
        month_day: int,
        leaderboard_uid: str,
        leaderboard: List[Dict] | None = None,
    ):
        """
        Constructor for the class
        """
        self.campaign_id = campaign_id
        self.map_author_id = map_author_id
        self.map_name = map_name
        self.map_type = map_type
        self.medal_times = medal_times
        self.map_id = map_id
        self.map_uid = map_uid
        self.timestamp = timestamp
        self.file_url = file_url
        self.thumbnail_url = thumbnail_url
        self.week_day = week_day
        self.month_day = month_day
        self.leaderboard_uid = leaderboard_uid
        self.leaderboard = leaderboard
