import json
from contextlib import suppress
from typing import Dict, List, Tuple
import logging

import redis

from ..api import APIClient
from ..config import Client
from ..constants import TMIO
from ..errors import InvalidIDError, InvalidMatchmakingGroupError, InvalidUsernameError
from ..structures.player import Player, PlayerSearchResult
from ..util import player_parsers

_log = logging.getLogger(__name__)


async def get_player(
    player_id: str, raw: bool = False
) -> Player | Tuple[Player, Dict] | None:
    """
    Retrieves a player's information using their player_id.

    Parameters
    ----------
    player_id : str
        The player_id to get the information for.
    raw : bool, optional
        Whether to return the raw data from the API alongside the parsed one, by default False

    Returns
    -------
    :class:`Player` | :class:`Tuple[Player, Dict]` | None
        The player's information.

    Raises
    ------
    `InvalidIDError`
        If the player_id is empty, or no player exists with that player_id.
    """
    cache_client = redis.Redis(
        host=Client.REDIS_HOST,
        port=Client.REDIS_PORT,
        db=Client.REDIS_DB,
        password=Client.REDIS_PASSWORD,
    )

    if player_id == "":
        raise InvalidIDError("The player id cannot be empty.")

    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        if cache_client.exists(f"{player_id}|data"):
            _log.debug(f"{player_id} was cached.")
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

    _log.debug(f"Sending GET request to {TMIO.build([TMIO.TABS.PLAYER, player_id])}")
    player_resp = await api_client.get(TMIO.build([TMIO.TABS.PLAYER, player_id]))
    await api_client.close()

    player_data = player_parsers.parse_player(player_resp)

    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        cache_client.set(f"{player_id}|data", json.dumps(player_resp), ex=600)
        cache_client.set(f"{player_data['name'].lower()}:id", player_id)
        cache_client.set(f"{player_id}:username", player_data["name"])

        _log.debug(f"Cached {player_id}.")

    if not raw:
        return Player(**player_data)
    else:
        return Player(**player_data), player_resp


async def search_player(
    username: str,
) -> None | PlayerSearchResult | List[PlayerSearchResult]:
    """
    Searches for a player's information using their username.

    Parameters
    ----------
    username : str
        The player's username to search for.

    Returns
    -------
    None | :class:`PlayerSearchResult` | :class:`List[PlayerSearchResult]`
        None if no players. `PlayerSearchResult` if only one player. `List`[`PlayerSearchResult`] if multiple players.

    Raises
    ------
    `InvalidUsernameError`
        if the username is empty.
    """
    if username == "":
        raise InvalidUsernameError("Usernmae cannot be empty.")

    api_client = APIClient()
    _log.debug(
        f"Sending GET request to {TMIO.build([TMIO.TABS.PLAYERS])}"
        + f"/find?search={username}"
    )
    search_result = await api_client.get(
        TMIO.build([TMIO.TABS.PLAYERS]) + f"/find?search={username}"
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
    Returns the account id of the given username.

    Parameters
    ----------
    username : str
        The username of the player.

    Returns
    -------
    str | None
        The id of the player.

    Raises
    ------
    ValueError
        If the username given is :class:`NoneType`.
    """
    cache_client = redis.Redis(
        host=Client.REDIS_HOST,
        port=Client.REDIS_PORT,
        db=Client.REDIS_DB,
        password=Client.REDIS_PASSWORD,
    )

    if username is None:
        raise ValueError("Username cannot be None.")

    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        if cache_client.exists(f"{username.lower()}|id"):
            _log.debug(f"{username} was cached.")
            return cache_client.get(f"{username.lower()}|id").decode("utf-8")

        player_data = await search_player(username)

        if player_data is None:
            return None
        if isinstance(player_data, PlayerSearchResult):
            with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
                cache_client.set(
                    f"{player_data.name.lower()}|id", player_data.player_id
                )
                _log.debug(f"Cached {player_data.name.lower()}.")

            return player_data.player_id

        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            cache_client.set(
                f"{player_data[0].name.lower()}|id", player_data[0].player_id
            )
            _log.debug(f"Cached {player_data[0].name.lower()}.")
        return player_data[0].player_id


async def to_username(player_id: str) -> str | None:
    """
    Gets a player's username from their ID.

    Parameters
    ----------
    player_id : str
        The ID of the player.

    Returns
    -------
    str | None
        The username of the player. `None` if the player doesn't exist.
    """
    cache_client = redis.Redis(
        host=Client.REDIS_HOST,
        port=Client.REDIS_PORT,
        db=Client.REDIS_DB,
        password=Client.REDIS_PASSWORD,
    )

    if player_id is None:
        raise ValueError("player_id cannot be NoneType")
    if not isinstance(player_id, str):
        raise ValueError("player_id must be a string")

    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        if cache_client.exists(f"{player_id}|username"):
            _log.debug(f"{player_id} was cached.")
            return cache_client.get(f"{player_id}|username").decode("utf-8")

    player = await get_player(player_id)

    if player is not None:
        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            cache_client.set(f"{player_id}|username", player.name)
            _log.debug(f"Cached {player_id}.")
        return player.name

    return None


async def top_matchmaking(group: int, page: int = 0) -> Dict:
    """
    Retrieves the

    Parameters
    ----------
    group : int
        The group id. 2 for 3v3 matchmaking and 3 for royal.
    page : int, optional
        The page of the leaderboard. Each page has 50 players. by default 0

    Returns
    -------
    :class:`Dict`
        The matchmaking data.

    Raises
    ------
    `InvalidMatchmakingGroupError`
        If the group is not 2 or 3.
    """
    cache_client = redis.Redis(
        host=Client.REDIS_HOST,
        port=Client.REDIS_PORT,
        db=Client.REDIS_DB,
        password=Client.REDIS_PASSWORD,
    )

    if int(group) not in (2, 3):
        raise InvalidMatchmakingGroupError("Matchmaking group should be 2 or 3.")
    if page < 0:
        raise ValueError("Page must be greater than or equal to 0.")

    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        if cache_client.exists(f"matchmaking|{group}|{page}"):
            _log.debug(f"{group} page: {page} was cached.")
            return json.loads(cache_client.get(f"matchmaking|{group}|{page}"))

    api_client = APIClient()
    _log.debug(
        f"Sending GET request to {TMIO.build([TMIO.TABS.TOP_MATCHMAKING, group, page])}"
    )
    matchmaking_resp = await api_client.get(
        TMIO.build([TMIO.TABS.TOP_MATCHMAKING, group, page])
    )
    await api_client.close()

    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        cache_client.set(
            f"matchmaking|{group}|{page}", json.dumps(matchmaking_resp), ex=3600
        )
        _log.debug(f"Cached {group} page: {page}.")

    return matchmaking_resp


async def top_trophies(page: int = 0) -> Dict:
    """
    Gets the trophy leaderboard.

    Parameters
    ----------
    page : int, optional
        Page for the leaderboard, each page contains 50 players. by default 0

    Returns
    -------
    :class:`Dict`
        The trophy leaderboard data.
    """
    if page < 0:
        raise ValueError("Page cannot be less than 0.")

    cache_client = redis.Redis(
        host=Client.REDIS_HOST,
        port=Client.REDIS_PORT,
        db=Client.REDIS_DB,
        password=Client.REDIS_PASSWORD,
    )

    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        if cache_client.exists(f"trophies|{page}"):
            _log.debug(f"trophies page: {page} was cached.")
            return json.loads(cache_client.get(f"trophies|{page}"))

    api_client = APIClient()
    _log.debug(f"Sending GET request to {TMIO.build([TMIO.TABS.TOP_TROPHIES, page])}")
    trophies_resp = await api_client.get(TMIO.build([TMIO.TABS.TOP_TROPHIES, page]))
    await api_client.close()

    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        cache_client.set(f"trophies|{page}", json.dumps(trophies_resp), ex=10800)
        _log.debug(f"Cached trophies page: {page}.")

    return trophies_resp
