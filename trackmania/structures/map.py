from typing import Dict, List

from .medal_times import MedalTimes
from .player import Player
from ..managers.player_manager import _parse_zones, _parse_meta

__all__ = ("TMMap", "TOTD", "TMMapLeaderboard")


class TMMap:
    """
    .. versionadded:: 0.1.0

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

class TMMapLeaderboard:
    """
    .. versionadded :: 0.3.0
    
    Represents a map leaderboard.
    
    Parameters
    ----------
    ghost : str
        File url for the ghost
    position : int
        The player's position
    time : int  
        The time in milliseconds
        
    Methods
    -------
    player() -> Player
    """

    def __init__(self, ghost: str, position: int, time: int, player: Player):
        self.ghost = ghost
        self.position = position
        self.time = time
        self._player = player
        
    @property
    def player(self):
        """
        .. versionadded :: 0.3.0
        
        Returns the player instance
        """
        return self._player
    
    @classmethod
    def from_dict(cls, raw_data: Dict):
        """
        .. versionadded:: 0.3.0
        
        Parses the dictionary data into a :class:`TMMapLeaderboard` object.

        Parameters
        ----------
        raw_data : Dict
            The raw data.

        Returns
        -------
        `TMMapLeaderboard`
            An instance of :class:`TMMapLeaderboard`
        """
        player_data = raw_data['player']
        player_obj_kwargs = {
            "club_tag": player_data['tag'] if 'tag' in player_data else None,
            "first_login": None,
            "id": player_data['id'],
            "last_club_tag_change": None,
            "login": player_data['name'],
            "meta": _parse_meta(player_data),
            "name": player_data['name'],
            "trophies": None,
            "zone": _parse_zones(player_data['zone']),
            "m3v3_data": None,
            "royal_data": None,
        }
        
        return cls(
            raw_data['url'],
            raw_data['position'],
            raw_data['time'],
            Player(**player_obj_kwargs)
        )

# pylint: disable=too-many-arguments, too-many-instance-attributes, too-few-public-methods
class TOTD(TMMap):
    """
    .. versionadded :: 0.3.0

    Represents a TOTD Map
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    