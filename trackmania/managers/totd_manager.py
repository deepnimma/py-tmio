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
from contextlib import suppress
from datetime import datetime
from typing import Dict, List

import redis

from trackmania.structures.map import TOTD

from ..api import APIClient
from ..config import Client
from ..constants import TMIO
from ..util import map_parsers


async def latest_totd(leaderboard_flag: bool = False) -> TOTD:
    """
    Fetches the current TOTD Map.

    :param leaderboard_flag: Whether to add the top 100 leaderboard to the data. If set to True, it makes another api request. Defaults to False
    :type leaderboard_flag: bool, optional
    :return: TOTD object
    :rtype: :class:`TOTD`

    Caching
    * Caches the latest_totd data for 1 hour unless it is past 5pm and before 6am. UTC
    """
    cache_client = redis.Redis(host=Client.redis_host, port=Client.redis_port)

    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        if cache_client.exists("latest_totd"):
            latest_totd = json.loads(cache_client.get("latest_totd"))
            return map_parsers.parse_totd_map(latest_totd, latest_totd["leaderboard"])

    api_client = APIClient()
    latest_totd = await api_client.get(TMIO.build([TMIO.tabs.totd, "0"]))
    latest_totd: dict = latest_totd["days"][-1]

    if leaderboard_flag:
        raw_lb_data = await api_client.get(
            TMIO.build(
                [TMIO.tabs.leaderboard, TMIO.tabs.map, latest_totd["map"]["mapUid"]]
            )
            + "?offset=0&length=100"
        )
        leaderboard = raw_lb_data["tops"]
    else:
        leaderboard = None

    await api_client.close()

    latest_totd.update({"leaderboard": leaderboard})

    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        hour, minute = datetime.utcnow().hour, datetime.utcnow().minute
        if not ((hour > 17 and minute > 0) and (hour < 18 and minute < 0)):
            cache_client.set(name="latest_totd", value=json.dumps(latest_totd), ex=3600)

    return map_parsers.parse_totd_map(latest_totd, leaderboard)


async def totd(
    year: int = 2022, month: int = 1, day: int = 1, leaderboard_flag: bool = False
) -> TOTD | List[Dict]:
    """
    Gets the TOTD of a specific day.

    :param year: The year of the TOTD, defaults to 2022. Acceptable values are 2020, 2021 and 2022.
    :type year: int, optional
    :param month: The month of the TOTD, defaults to 1 for January. Acceptable values are in the range 1-12.
    :type month: int, optional
    :param day: The day of the TOTD, defaults to 1. Acceptable values are 1-31. If the day is -1 then all totds of the month are returned.
    :type day: int, optional
    :param leaderboard_flag: Whether to add the top 100 leaderboard to the data. If set to True, it makes another api request. Defaults to False
    :type leaderboard_flag: bool, optional
    """

    # Date Checks
    today_date = datetime.utcnow()

    if year not in (2020, 2021, 2022):
        raise ValueError("Year must be 2020, 2021 or 2022")
    if month not in range(1, 13):
        raise ValueError("Month must be in the range 1-12")
    if day not in range(-1, 31) or day == 0:
        raise ValueError("Day cannot be greater than 31")
    if today_date.year == year and today_date.month < month:
        raise ValueError("Month must be in the past")
    if today_date.year == year and today_date.month == month and today_date.day < day:
        raise ValueError("Day must be in the past.")
    if month == 2 and year % 4 != 0 and day > 28:
        raise ValueError("February only has 28 days in a non-leap year.")
    if month == 2 and year % 4 == 0 and day > 29:
        raise ValueError("February only has 29 days in a leap year.")
    if month % 2 == 0 and day > 30:
        raise ValueError("This month (%s) only has 30 days." % month)
    if year == 2020 and month < 7:
        raise ValueError("TM2020 Released on July 1st.")

    cache_client = redis.Redis(host=Client.redis_host, port=Client.redis_port)

    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        if day == -1 and cache_client.exists(f"totd|{year}|{month}|-1"):
            return json.loads(cache_client.get(f"totd|{year}|{month}|-1"))

        if cache_client.exists(f"totd|{year}|{month}|{day}"):
            totd = cache_client.get(f"totd|{year}|{month}|{day}")
            return map_parsers.parse_totd_map(json.loads(totd, totd["leaderboard"]))

    # Find how many months ago the given month is.
    count = 0

    if year == 2020:
        count = (12 - month) + 12 + today_date.month
    elif year == 2021:
        count = (12 - month) + today_date.month
    else:
        count = today_date.month - month

    api_client = APIClient()
    month_data = await api_client.get(TMIO.build([TMIO.tabs.totd, str(count)]))

    if day == -1:
        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            cache_client.set(
                f"totd|{year}|{month}|-1",
                json.dumps(month_data),
                ex=None if count != 0 else 14400,
            )
        return month_data["days"]

    if leaderboard_flag:
        raw_lb_data = await api_client.get(
            TMIO.build(
                [
                    TMIO.tabs.leaderboard,
                    TMIO.tabs.map,
                    month_data["days"][day - 1]["map"]["mapUid"],
                ]
            )
            + "?offset=0&length=100"
        )
        leaderboard = raw_lb_data["tops"]
    else:
        leaderboard = None
    await api_client.close()

    month_data["days"][day - 1].update({"leaderboard": leaderboard})

    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        cache_client.set(
            f"totd|{year}|{month}|{day}",
            json.dumps(month_data["days"][day - 1]),
            ex=None if count != 0 else 14400,
        )
    return map_parsers.parse_totd_map(month_data["days"][day - 1], leaderboard)
