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

from .medal_times import MedalTimes

__all__ = ("TOTD",)

# pylint: disable=too-many-arguments, too-many-instance-attributes, too-few-public-methods
class TOTD:
    """
    Class that represents a totd map
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
