"""
MIT License

Copyright (c) 2022-present Deepesh Nimma

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from typing import Dict, List

from ..structures.map import TOTD
from ..structures.medal_times import MedalTimes


def parse_totd_map(map_data: Dict, leaderboard: List[Dict] | None = None) -> TOTD:
    """
    Parses TOTD Map Data.

    :param map_data: The map data as a dict or json.
    :type map_data: :class:`Dict`
    :return: The TOTD object for the map.
    :rtype: :class:`TOTD`
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
