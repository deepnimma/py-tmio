import json
from contextlib import suppress
from typing import Dict, List, Tuple
import logging

import redis

from ..api import APIClient
from ..config import Client
from ..constants import TMIO
from ..errors import InvalidIDError, InvalidMatchmakingGroupError, InvalidUsernameError
from ..structures.player import (
    Player,
    PlayerSearchResult,
    PlayerTrophies,
    PlayerMatchmaking,
    PlayerMetaInfo,
    PlayerZone,
)

_log = logging.getLogger(__name__)


async def get_player(
    player_id: str, raw: bool = False
) -> Player | Tuple[Player, Dict] | None:
    """
    .. versionadded:: 0.1.0

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
                **_parse_player(json.loads(cache_client.get(f"{player_id}|data")))
            )
            if not raw:
                return player
            if raw:
                return player, json.loads(cache_client.get(f"{player_id}|data"))

    api_client = APIClient()

    _log.debug(f"Sending GET request to {TMIO.build([TMIO.TABS.PLAYER, player_id])}")
    player_resp = await api_client.get(TMIO.build([TMIO.TABS.PLAYER, player_id]))
    await api_client.close()

    player_data = _parse_player(player_resp)

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
    .. versionadded:: 0.1.0

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
        return PlayerSearchResult(**__parse_search_results(search_result[0]))

    results = []

    for player_data in search_result:
        results.append(PlayerSearchResult(**__parse_search_results(player_data)))
    return results


async def to_account_id(username: str) -> str | None:
    """
    .. versionadded:: 0.1.0

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
    .. versionadded:: 0.1.0

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
    .. versionadded:: 0.1.0

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
    .. versionadded:: 0.1.0

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


def _parse_player(data: Dict) -> Tuple:
    """
    .. versionadded:: 0.1.0

    Parses the JSON data into the required data types for the :class:`Player` constructor.

    Parameters
    ----------
    data : :class:`Dict`
        The JSON data to parse.

    Returns
    -------
    :class:`Tuple`
        The parsed data as a tuple.
    """

    display_name = data["displayname"]
    player_id = data["accountid"]
    first_login = data["timestamp"]

    try:
        club_tag = data["clubtag"]
        club_tag_timestamp = data["clubtagtimestamp"]
    except KeyError:
        club_tag, club_tag_timestamp = None, None
    trophy_points = data["trophies"]["points"]
    trophy_count = data["trophies"]["counts"]
    last_trophy = data["trophies"]["timestamp"]
    echelon = data["trophies"]["echelon"]

    zones = data["trophies"]["zone"]
    zone_positions = data["trophies"]["zonepositions"]

    try:
        player_meta = _parse_meta(data["meta"])
    except KeyError:
        player_meta = None

    player_trophies = PlayerTrophies(
        echelon, last_trophy, trophy_points, trophy_count, player_id
    )
    player_zones = _parse_zones(zones, zone_positions)

    player_mm_data = __parse_matchmaking(data["matchmaking"])
    threes, royal = player_mm_data[0], player_mm_data[1]

    return {
        "club_tag": club_tag,
        "first_login": first_login,
        "player_id": player_id,
        "last_club_tag_change": club_tag_timestamp,
        "login": display_name,
        "meta": player_meta,
        "name": display_name,
        "trophies": player_trophies,
        "zone": player_zones,
        "m3v3_data": threes,
        "royal_data": royal,
    }


def _parse_zones(zones: Dict, zone_positions: List[int]) -> List[PlayerZone]:
    """Parses the Data from the API into a list of PlayerZone objects.

    Parameters
    ----------
    zones : :class:`Dict`
        the zones data from the API.
    zone_positions : :class:`List[int]`
        The zone positions data from the API.

    Returns
    -------
    class:`List[PlayerZone]`
        The list of :class:`PlayerZone` objects.

    """
    player_zone_list = []

    if len(zone_positions) == 3:
        player_zone_list.append(
            PlayerZone(zones["flag"], zones["name"], zone_positions[0])
        )
        player_zone_list.append(
            PlayerZone(
                zones["parent"]["flag"], zones["parent"]["name"], zone_positions[1]
            )
        )
        player_zone_list.append(
            PlayerZone(
                zones["parent"]["parent"]["flag"],
                zones["parent"]["parent"]["name"],
                zone_positions[2],
            )
        )
    elif len(zone_positions) == 4:
        player_zone_list.append(
            PlayerZone(zones["flag"], zones["name"], zone_positions[0])
        )
        player_zone_list.append(
            PlayerZone(
                zones["parent"]["flag"], zones["parent"]["name"], zone_positions[1]
            )
        )
        player_zone_list.append(
            PlayerZone(
                zones["parent"]["parent"]["flag"],
                zones["parent"]["parent"]["name"],
                zone_positions[2],
            )
        )
        player_zone_list.append(
            PlayerZone(
                zones["parent"]["parent"]["parent"]["flag"],
                zones["parent"]["parent"]["parent"]["name"],
                zone_positions[3],
            )
        )
    elif len(zone_positions) == 5:
        player_zone_list.append(
            PlayerZone(zones["flag"], zones["name"], zone_positions[0])
        )
        player_zone_list.append(
            PlayerZone(
                zones["parent"]["flag"], zones["parent"]["name"], zone_positions[1]
            )
        )
        player_zone_list.append(
            PlayerZone(
                zones["parent"]["parent"]["flag"],
                zones["parent"]["parent"]["name"],
                zone_positions[2],
            )
        )
        player_zone_list.append(
            PlayerZone(
                zones["parent"]["parent"]["parent"]["flag"],
                zones["parent"]["parent"]["parent"]["name"],
                zone_positions[3],
            )
        )
        player_zone_list.append(
            PlayerZone(
                zones["parent"]["parent"]["parent"]["parent"]["flag"],
                zones["parent"]["parent"]["parent"]["parent"]["name"],
                zone_positions[4],
            )
        )
    else:
        player_zone_list = None

    return player_zone_list


def _parse_meta(metadata: Dict) -> PlayerMetaInfo:
    """
    Parses the Meta Data from the API into a :class:`PlayerMetaInfo` object.

    Parameters
    ----------
    metadata : :class:`Dict`
        The meta data from the api.

    Returns
    -------
    :class:`PlayerMetaInfo`
        The parsed data.
    """
    # Please someone teach me a better way of doing this...
    try:
        twitter = metadata["twitter"]
    except KeyError:
        twitter = None

    try:
        twitch = metadata["twitch"]
    except KeyError:
        twitch = None

    try:
        youtube = metadata["youtube"]
    except KeyError:
        youtube = None

    try:
        vanity = metadata["vanity"]
    except KeyError:
        vanity = None

    try:
        sponsor = metadata["sponsor"]
        sponsor_level = metadata["sponsorlevel"]
    except KeyError:
        sponsor = False
        sponsor_level = 0

    try:
        nadeo = metadata["nadeo"]
    except KeyError:
        nadeo = False

    try:
        tmgl = metadata["tmgl"]
    except KeyError:
        tmgl = False

    try:
        team = metadata["team"]
    except KeyError:
        team = False

    return PlayerMetaInfo(
        vanity,
        nadeo,
        tmgl,
        team,
        sponsor,
        sponsor_level,
        twitch,
        twitter,
        youtube,
        vanity,
    )


def __parse_matchmaking(data: List[Dict]) -> List[PlayerMatchmaking]:
    """
    Parses the matchmaking data of the player and returns 2 :class:`PlayerMatchmaking` objects.
        One for 3v3 Matchmaking and the other for Royal matchmaking.

    Parameters
    ----------
    data : :class:`List[Dict]`
        The matchmaking data.

    Returns
    -------
    :class:`List[PlayerMatchmaking]`
        The list of matchmaking data, one for 3v3 and other other one for royal.
    """
    matchmaking_data = []

    try:
        matchmaking_data.append(__parse_3v3(data[0]))
    except (KeyError, IndexError):
        matchmaking_data.append(None)

    try:
        matchmaking_data.append(__parse_3v3(data[1]))
    except (KeyError, IndexError):
        matchmaking_data.append(None)

    return matchmaking_data


def __parse_3v3(data: Dict) -> PlayerMatchmaking:
    """
    Parses matchmaking data for 3v3 and royal type matchmaking.

    Parameters
    ----------
    data : :class:`Dict`
        The matchmaking data only.

    Returns
    -------
    :class:`PlayerMatchmaking`
        The parsed data.
    """
    typename = data["info"]["typename"]
    typeid = data["info"]["typeid"]
    rank = data["info"]["rank"]
    score = data["info"]["score"]
    progression = data["info"]["progression"]
    division = data["info"]["division"]["position"]
    min_points = data["info"]["division"]["minpoints"]
    max_points = data["info"]["division"]["maxpoints"]

    return PlayerMatchmaking(
        typename, typeid, progression, rank, score, division, min_points, max_points
    )


def __parse_search_results(data: Dict) -> PlayerSearchResult:
    """
    Parses the search result of a single player.

    Parameters
    ----------
    data : :class:`Dict`
        Player data.

    Returns
    -------
    :class:`PlayerSearchResult`
        Parsed player data.
    """
    name = data["player"]["name"]
    player_id = data["player"]["id"]

    try:
        club_tag = data["player"]["tag"]
    except KeyError:
        club_tag = None

    try:
        zone_data = __parse_search_zones(data["player"]["zone"])
    except KeyError:
        zone_data = [
            PlayerZone(None, None, None),
            PlayerZone(None, None, None),
            PlayerZone(None, None, None),
            PlayerZone(None, None, None),
            PlayerZone(None, None, None),
        ]
    try:
        matchmaking_data = __parse_matchmaking(data["player"]["matchmaking"])
    except KeyError:
        matchmaking_data = [None, None]

    return {
        "club_tag": club_tag,
        "name": name,
        "player_id": player_id,
        "zone": zone_data,
        "threes": matchmaking_data[0],
        "royal": matchmaking_data[1],
    }


def __parse_search_zones(zones: Dict) -> List[PlayerZone]:
    """Parses the zones for search result. A seperate function because search result does not have the zone positions.

    Parameters
    ----------
    zones : :class:`Dict`
        Zone data

    Returns
    -------
    :class:`List[PlayerZone]`
        The list of PlayerZone objects to represent the zone data. Zone positions are set as -1.
    """
    player_zone_list = []

    player_zone_list.append(PlayerZone(zones["flag"], zones["name"], -1))
    player_zone_list.append(
        PlayerZone(zones["parent"]["flag"], zones["parent"]["name"], -1)
    )
    player_zone_list.append(
        PlayerZone(
            zones["parent"]["parent"]["flag"], zones["parent"]["parent"]["name"], -1
        )
    )

    try:
        player_zone_list.append(
            PlayerZone(
                zones["parent"]["parent"]["parent"]["flag"],
                zones["parent"]["parent"]["parent"]["name"],
                -1,
            )
        )

        try:
            player_zone_list.append(
                PlayerZone(
                    zones["parent"]["parent"]["parent"]["parent"]["flag"],
                    zones["parent"]["parent"]["parent"]["parent"]["name"],
                    -1,
                )
            )
        except KeyError:
            pass
    except KeyError:
        pass

    return player_zone_list
