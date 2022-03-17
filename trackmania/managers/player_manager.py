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
from typing import Dict, List, Tuple

import redis

from ..api import APIClient
from ..config import Client
from ..constants import TMIO
from ..errors import InvalidIDError, InvalidMatchmakingGroupError, InvalidUsernameError
from ..structures.player import Player, PlayerSearchResult
from ..util import player_parsers


async def get_player(
    player_id: str, raw: bool = False
) -> Player | Tuple[Player, Dict] | None:
    """
    Retrieves a player's information using their player_id

    :param player_id: The player id to get information for.
    :type player_id: str
    :param raw: Whether to return the raw data from the API.
    :type raw: bool
    :raises :class:`InvalidIDError`: if the player id is empty, or no player exists with that player_id.
    :return: The player's information
    :rtype: :class:`Player` | :class:`Tuple`[:class:`Player`, :class:`Dict`] | None

    Caching
    * Caches the player information for 10 minutes.
    * Caches `username:player_id` pair forever.
    * Caches `player_id:username` pair forever.
    """
    cache_client = redis.Redis(host=Client.redis_host, port=Client.redis_port)

    if player_id == "":
        raise InvalidIDError("The player id cannot be empty.")

    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        if cache_client.exists(f"{player_id}|data"):
            player = Player(
                **player_parsers.parse_player(
                    json.loads(cache_client.get(f"{player_id}|data"))
                )
            )
            if not raw:
                return player
            if raw:
                return player, json.loads(cache_client.get(f"{player_id}|data"))
    api_client = APIClient()
    player_resp = await api_client.get(TMIO.build([TMIO.tabs.player, player_id]))
    await api_client.close()

    player_data = player_parsers.parse_player(player_resp)

    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        cache_client.set(f"{player_id}|data", json.dumps(player_resp), ex=600)
        cache_client.set(f"{player_data['name'].lower()}:id", player_id)
        cache_client.set(f"{player_id}:username", player_data["name"])

    if not raw:
        return Player(**player_data)
    else:
        return tuple(Player(**player_data), player_resp)


async def search_player(
    username: str,
) -> None | PlayerSearchResult | List[PlayerSearchResult]:
    """
    Searches for a player's information

    :param username: The player's username to search for.
    :type username: str
    :raises :class:`InvalidUsernameError`: If the username is empty or if there is no users with this username.
    :return: None if no players. :class:`PlayerSearchResult` if one player. List of :class:`PlayerSearchResult` if multiple players.
    :rtype: None|:class:`PlayerSearchResult`|:class:`List`[:class:`PlayerSearchResult`]
    """
    cache_client = redis.Redis(host=Client.redis_host, port=Client.redis_port)

    if username == "":
        raise InvalidUsernameError("Usernmae cannot be empty.")

    api_client = APIClient()
    search_result = await api_client.get(
        TMIO.build([TMIO.tabs.players]) + f"/find?search={username}"
    )
    await api_client.close()

    try:
        raise InvalidUsernameError(search_result["error"])
    except (KeyError, TypeError):
        pass

    if len(search_result) == 0:
        return None
    if len(search_result) == 1:
        return PlayerSearchResult(
            **player_parsers._parse_search_results(search_result[0])
        )

    results = []

    for player_data in search_result:
        results.append(
            PlayerSearchResult(**player_parsers._parse_search_results(player_data))
        )
    return results


async def to_account_id(username: str) -> str | None:
    """
    Returns the account id of the given username

    :param username: The username of the player.
    :type username: str
    :return: The id of the player.
    :rtype: str | None

    Caching

    * Caches `username:player_id` pair forever.
    * Caches `player_id:username` pair forever.
    """
    cache_client = redis.Redis(host=Client.redis_host, port=Client.redis_port)

    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        if cache_client.exists(f"{username.lower()}|id"):
            return cache_client.get(f"{username.lower()}|id").decode("utf-8")

        player_data = await search_player(username)

        if player_data is None:
            return None
        if isinstance(player_data, PlayerSearchResult):
            with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
                cache_client.set(
                    f"{player_data.name.lower()}|id", player_data.player_id
                )

            return player_data.player_id

        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            cache_client.set(
                f"{player_data[0].name.lower()}|id", player_data[0].player_id
            )
        return player_data[0].player_id


async def to_username(player_id: str) -> str | None:
    """
    Gets a player's username from their ID.

    :param player_id: The ID of the player.
    :type player_id: str
    :return: The player's username, None if the player does not exist.
    :rtype: str | None
    """
    cache_client = redis.Redis(host=Client.redis_host, port=Client.redis_port)

    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        if cache_client.exists(f"{player_id}|username"):
            return cache_client.get(f"{player_id}|username").decode("utf-8")

    player = await get_player(player_id)

    if player is not None:
        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            cache_client.set(f"{player_id}|username", player.name)
        return player.name

    return None


async def top_matchmaking(group: int, page: int = 0):
    """
    Retrieves the Matchmaking leaderboard.

    :param group: The group id, 2 is 3v3 matchmaking and 3 is royal matchmaking.
    :type group: int
    :param page: The page of the leaderboard. Each number is 50 users, defaults to 0
    :type page: int, optional

    Caching

    Caches each page for 1 hour.
    """
    cache_client = redis.Redis(host=Client.redis_host, port=Client.redis_port)

    if int(group) not in (2, 3):
        raise InvalidMatchmakingGroupError("Matchmaking group should be 2 or 3.")

    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        if cache_client.exists(f"matchmaking|{group}|{page}"):
            return json.loads(cache_client.get(f"matchmaking|{group}|{page}"))

    api_client = APIClient()
    matchmaking_resp = await api_client.get(
        TMIO.build([TMIO.tabs.top_matchmaking, group, page])
    )
    await api_client.close()

    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        cache_client.set(
            f"matchmaking|{group}|{page}", json.dumps(matchmaking_resp), ex=3600
        )

    return matchmaking_resp


async def top_trophies(page: int = 0):
    """
    Gets the Trophy leaderboard.

    :param page: Page for the leaderboard, each page contains 50 players. defaults to 0
    :type page: int, optional

    Caching

    Caches trophy leaderboard page for 3 hr
    """
    cache_client = redis.Redis(host=Client.redis_host, port=Client.redis_port)

    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        if cache_client.exists(f"trophies|{page}"):
            return json.loads(cache_client.get(f"trophies|{page}"))

    api_client = APIClient()
    trophies_resp = await api_client.get(TMIO.build([TMIO.tabs.top_trophies, page]))
    await api_client.close()

    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        cache_client.set(f"trophies|{page}", json.dumps(trophies_resp), ex=10800)

    return trophies_resp
