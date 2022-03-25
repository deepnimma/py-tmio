from typing import Dict, List

from ..structures.map import TOTD
from ..structures.medal_times import MedalTimes


def parse_totd_map(map_data: Dict, leaderboard: List[Dict] | None = None) -> TOTD:
    """Parses TOTD Map Data.

    :param map_data (: class:`Dict`): The map data as a dict or json.
    :param map_data: Dict:
    :param leaderboard: List[Dict] | None:  (Default value = None)
    :returns: class:`TOTD`: The TOTD object for the map.

    Parameters
    ----------
    map_data : :class:`Dict`
        The map data as a dict or json.
    leaderboard: :class:`List[Dict]` | None :
         (Default value = None)

    Returns
    -------
    class:`TOTD`
        The TOTD object for the map.

    """
    campaign_id = map_data["campaignid"]
    map_author_id = map_data["map"]["author"]
    map_name = map_data["map"]["name"]
    map_type = map_data["map"]["mapType"]

    medal_times = MedalTimes(
        map_data["map"]["bronzeScore"],
        map_data["map"]["silverScore"],
        map_data["map"]["goldScore"],
        map_data["map"]["authorScore"],
    )

    map_id = map_data["map"]["mapId"]
    map_uid = map_data["map"]["mapUid"]
    timestamp = map_data["map"]["timestamp"]
    file_url = map_data["map"]["fileUrl"]
    thumbnail_url = map_data["map"]["thumbnailUrl"]
    week_day = map_data["weekday"]
    month_day = map_data["monthday"]
    leaderboard_uid = map_data["leaderboarduid"]

    return TOTD(
        campaign_id,
        map_author_id,
        map_name,
        map_type,
        medal_times,
        map_id,
        map_uid,
        timestamp,
        file_url,
        thumbnail_url,
        week_day,
        month_day,
        leaderboard_uid,
        leaderboard,
    )
