# pylint: disable=too-many-locals

from __future__ import division

from typing import Dict, List, Tuple

from trackmania.structures.player import PlayerSearchResult

from ..structures.player import (
    PlayerMatchmaking,
    PlayerMetaInfo,
    PlayerTrophies,
    PlayerZone,
)


def parse_player(data: Dict) -> Tuple:
    """
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

    player_mm_data = _parse_matchmaking(data["matchmaking"])
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


def _parse_matchmaking(data: List[Dict]) -> List[PlayerMatchmaking]:
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


def _parse_search_results(data: Dict) -> PlayerSearchResult:
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
        zone_data = _parse_search_zones(data["player"]["zone"])
    except KeyError:
        zone_data = [
            PlayerZone(None, None, None),
            PlayerZone(None, None, None),
            PlayerZone(None, None, None),
            PlayerZone(None, None, None),
            PlayerZone(None, None, None),
        ]
    try:
        matchmaking_data = _parse_matchmaking(data["player"]["matchmaking"])
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


def _parse_search_zones(zones: Dict) -> List[PlayerZone]:
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
