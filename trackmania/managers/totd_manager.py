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

import redis

from trackmania.structures.map import TOTD

from ..api import APIClient
from ..config import Client
from ..constants import TMIO
from ..util import map_parsers


async def latest() -> TOTD:
    """
    Fetches the current totd map

    :return: TOTD object
    :rtype: :class:`TOTD`

    Caching
    -------
    * Caches the latest_totd data for 1 hour unless it is past 10:30pm
    """
    cache_client = redis.Redis(host=Client.redis_host, port=Client.redis_port)

    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        if cache_client.exists("latest_totd"):
            return map_parsers.parse_totd_map(
                json.loads(cache_client.get("latest_totd"))
            )

    api_client = APIClient()
    latest_totd = await api_client.get(TMIO.build([TMIO.tabs.totd, "0"]))["days"][-1]
    await api_client.close()

    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        if (datetime.now().hour() > 22 and datetime.now().minute() > 30) and (
            datetime.now().hour() < 23 and datetime.now().minute() < 30
        ):
            cache_client.set(name="latest_totd", value=json.dumps(latest_totd), ex=3600)

    return map_parsers.parse_totd_map(latest_totd)
