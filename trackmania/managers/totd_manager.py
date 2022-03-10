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
import json
from datetime import datetime

import redis

from trackmania.structures.map import TOTD

from ..api import APIClient
from ..config import cache_client
from ..constants import TMIO
from ..util.map_parsers import MapParsers

__all__ = ("TotdManager",)

# pylint: disable=too-few-public-methods
class TotdManager:
    """
    TotdManager is a class that handles functions related to totd map
    """

    @staticmethod
    async def latest() -> TOTD:
        """
        Fetches the current totd map

        :return: TOTD object
        :rtype: :class:`TOTD`

        Caching
        -------
        * Caches the latest_totd data for 1 hour unless it is past 10:30pm
        """
        try:
            totd = cache_client.get("latest_totd")
        except (ConnectionRefusedError, redis.exceptions.ConnectionError):
            totd = None

        if totd is not None:
            return MapParsers.parse_totd_map(json.loads(totd))

        api_client = APIClient()

        latest_totd_url = TMIO.build([TMIO.tabs.totd, "0"])
        latest_month_totds = await api_client.get(latest_totd_url)

        await api_client.close()

        latest_totd = latest_month_totds["days"][-1]

        try:
            if (datetime.now().hour() > 22 and datetime.now().minute() > 30) and (
                datetime.now().hour() < 23 and datetime.now().minute() < 30
            ):
                cache_client.set(
                    name="latest_totd", value=json.dumps(latest_totd), ex=3600
                )
        except (ConnectionRefusedError, redis.exceptions.ConnectionError):
            pass

        return MapParsers.parse_totd_map(latest_totd)
