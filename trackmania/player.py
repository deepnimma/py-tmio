import json
import logging
from contextlib import suppress
from datetime import datetime
from typing import Dict, List

import redis

from .api import APIClient
from .config import Client
from .constants import TMIO
from .errors import TMIOException
from .matchmaking import PlayerMatchmaking
from .trophy import PlayerTrophies

_log = logging.getLogger(__name__)

__all__ = (
    "PlayerMetaInfo",
    "PlayerZone",
    "PlayerMatchmaking",
    "Player",
)


class PlayerMetaInfo:
    """
    .. versionadded :: 0.1.0

    Represents Player Meta Data, which inclues YT, Twitch, Twitter or TMIO Vanity Link

    Parameters
    ----------
    display_url : str
        The URL to the player's profile
    in_nadeo : bool
        Whether the player is in Nadeo
    in_tmgl : bool
        Whether the player is in TMGL
    in_tmio_dev_team : bool
        Whether the player is in TMIO Dev Team
    is_sponsor : bool
        Whether the player is a sponsor
    sponsor_level : int | None
        The sponsor level of the player
    twitch : str | None
        The Twitch URL of the player, `NoneType` if the player has no Twitch
    twitter : str | None
        The Twitter URL of the player, `NoneType` if the player has no Twitter
    youtube : str | None
        The YouTube URL of the player, `NoneType` if the player has no YouTube
    vanity : str | None
        The TMIO Vanity URL of the player, `NoneType` if the player has no TMIO Vanity URL
    """

    def __init__(
        self,
        display_url: str,
        in_nadeo: bool,
        in_tmgl: bool,
        in_tmio_dev_team: bool,
        is_sponsor: bool,
        sponsor_level: int | None,
        twitch: str | None,
        twitter: str | None,
        youtube: str | None,
        vanity: str | None,
    ):
        """
        Constructor method.
        """
        self.display_url = display_url
        self.in_nadeo = in_nadeo
        self.in_tmgl = in_tmgl
        self.in_tmio_dev_team = in_tmio_dev_team
        self.is_sponsor = is_sponsor
        self.sponsor_level = sponsor_level
        self.twitch = twitch
        self.twitter = twitter
        self.youtube = youtube
        self.vanity = vanity

    @classmethod
    def _from_dict(cls, meta_data: Dict):
        """
        Parses the meta data into a PlayerMetaInfo object.

        Parameters
        ----------
        meta_data : Dict
            The meta data to parse
        Returns
        -------
        :class:`PlayerMetaInfo`
            The parsed meta data
        """
        _log.debug(f"Creating a PlayerMetaInfo class from the given dictionary.")

        return cls(
            display_url=meta_data["display_url"]
            if "display_url" in meta_data
            else None,
            in_nadeo=meta_data["nadeo"] if "nadeo" in meta_data else False,
            in_tmgl=meta_data["tmgl"] if "tmgl" in meta_data else False,
            in_tmio_dev_team=meta_data["team"] if "team" in meta_data else False,
            is_sponsor=meta_data["sponsor"] if "sponsor" in meta_data else False,
            sponsor_level=meta_data["sponsor_level"]
            if "sponsor_level" in meta_data
            else 0,
            twitch=meta_data["twitch"] if "twitch" in meta_data else None,
            twitter=meta_data["twitter"] if "twitter" in meta_data else None,
            youtube=meta_data["youtube"] if "youtube" in meta_data else None,
            vanity=meta_data["vanity"] if "vanity" in meta_data else None,
        )


class PlayerZone:
    """
    .. versionadded :: 0.1.0

    Class that represents the player zone

    Parameters
    ----------
    flag : str
        The flag of the zone
    zone : str
        The zone name
    rank : int
        The rank of the player in the zone
    """

    def __init__(self, flag: str, zone: str, rank: int):
        """Constructor method."""
        self.flag = flag
        self.zone = zone
        self.rank = rank

    @classmethod
    def _parse_zones(cls, zones: Dict, zone_positions: List[int]) -> List:
        """
        Parses the Data from the API into a list of PlayerZone objects.

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
        _log.debug("Parsing Zones")
        player_zone_list: List = list()
        i: int = 0

        while "zone" in zones:
            _log.debug(f"Gone {i} Levels Deep")
            player_zone_list.append(
                cls(zones["flag"], zones["zone"], zone_positions[i])
            )
            i += 1

            if "parent" in zones:
                zones = zones["parent"]
            else:
                break

        return player_zone_list


class PlayerSearchResult:
    """
    .. versionadded :: 0.1.0

    Represents 1 Player from a Search Result

    Parameters
    ----------
    club_tag : str | None.
        The club tag of the player, `NoneType` if the player is not in a club.
    name : str
        Name of the player.
    player_id : str
        The Trackmania ID of the player.
    zone : :class:`List[PlayerZone]`, optional
        The zone of the player as a list.
    threes : :class:`PlayerMatchmaking`, optional
        The 3v3 data of the player.
    royals : :class:`PlayerMatchmaking`, optional
        The royal data of the player.
    """

    def __init__(
        self,
        club_tag: str | None,
        name: str,
        player_id: str,
        zone: List[PlayerZone],
        threes: PlayerMatchmaking | None,
        royal: PlayerMatchmaking | None,
    ):
        self.club_tag = club_tag
        self.name = name
        self.player_id = player_id
        self.zone = zone
        self.threes = threes
        self.royal = royal

    @classmethod
    def _from_dict(cls, player_data: Dict):
        zone = (
            PlayerZone._parse_zones(player_data["player"]["zone"], [0, 0, 0, 0, 0])
            if "zone" in player_data
            else None
        )
        club_tag = (
            player_data["player"]["club_tag"]
            if "club_tag" in player_data["player"]
            else None
        )
        name = player_data["player"]["name"]
        player_id = player_data["player"]["id"]
        matchmaking = PlayerMatchmaking._from_dict(
            player_data["matchmaking"], player_id
        )

        return cls(club_tag, name, player_id, zone, matchmaking[0], matchmaking[1])


class Player:
    """
    .. versionadded :: 0.1.0

    Represents a Player in Trackmania

    Parameters
    ----------
    club_tag : str | None.
        The club tag of the player, `NoneType` if the player is not in a club.
    first_login : :class:`datetime` | None
        The date of the first login of the player.
    player_id : str
        The Trackmania ID of the player.
    last_club_tag_change : str
        The date of the last club tag change of the player.
    login : str
        Login of the player.
    meta : :class:`PlayerMetaInfo`.
        Meta data of the player.
    name : str
        Name of the player.
    trophies : :class:`PlayerTrophies`, optional
        The trophies of the player.
    zone : :class:`List[PlayerZone]`, optional
        The zone of the player as a list.
    m3v3_data : :class:`PlayerMatchmaking`, optional
        The 3v3 data of the player.
    royal_data : :class:`PlayerMatchmaking`, optional
        The royal data of the player.
    """

    def __init__(
        self,
        club_tag: str | None,
        first_login: datetime | None,
        player_id: str,
        last_club_tag_change: str,
        meta: PlayerMetaInfo,
        name: str,
        trophies: PlayerTrophies | None = None,
        zone: List[PlayerZone] | None = None,
        m3v3_data: PlayerMatchmaking | None = None,
        royal_data: PlayerMatchmaking | None = None,
    ):
        """Constructor of the class."""
        self.club_tag = club_tag
        self._first_login = first_login
        self._id = player_id
        self.last_club_tag_change = last_club_tag_change
        self.meta = meta
        self.name = name
        self.trophies = trophies
        self.zone = zone
        self.m3v3_data = m3v3_data
        self.royal_data = royal_data

    def __str__(self):
        """String representation of the class."""
        return f"Player: {self.name} ({self.login})"

    @property
    def first_login(self):
        """first login property."""
        return self._first_login

    @property
    def player_id(self):
        """player id property."""
        return self._id

    @classmethod
    async def get(cls, player_id: str):
        """
        .. versionadded :: 0.1.0

        Gets a player's data from their player_id

        Parameters
        ----------
        player_id : str
            The player id of the player
        """
        _log.debug(f"Getting {player_id}'s data")

        cache_client = redis.Redis(
            host=Client.REDIS_HOST,
            port=Client.REDIS_PORT,
            db=Client.REDIS_DB,
            password=Client.REDIS_PASSWORD,
        )

        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            if cache_client.exists(f"player:{player_id}"):
                _log.debug(f"{player_id}'s data found in cache")
                player_data = cache_client.get(f"player:{player_id}").decode("utf-8")
                player_data = json.loads(player_data)
                return cls(
                    **Player._parse_player(
                        json.loads(
                            cache_client.get(f"player:{player_id}").decode("utf-8")
                        )
                    )
                )

        api_client = APIClient()
        player_data = await api_client.get(TMIO.build([TMIO.TABS.PLAYER, player_id]))
        await api_client.close()

        with suppress(KeyError, TypeError):
            _log.error("This is a trackmania.io error")
            raise TMIOException(player_data["error"])
        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            cache_client.set(f"player:{player_id}", json.dumps(player_data))
            cache_client.set(f"{player_data['displayname'].lower()}:id", player_id)

        return cls(**Player._parse_player(player_data))

    @staticmethod
    async def search(
        username: str,
    ) -> None | PlayerSearchResult | List[PlayerSearchResult]:
        """
        .. versionadded :: 0.1.0

        Searches for a player's information using their username.

        Parameters
        ----------
        username : str
            The player's username to search for

        Returns
        -------
        :class:`NoneType` | :class:`PlayerSearchResult` | :class:`List[PlayerSearchResult]`
            None if no players. :class:`PlayerSearchResult` if only one player. :class:`List[PlayerSearchResult]` if multiple players.
        """
        _log.debug(f"Searching for players with the username -> {username}")

        api_client = APIClient()
        search_result = await api_client.get(
            TMIO.build([TMIO.TABS.PLAYERS]) + f"/find?search={username}"
        )
        await api_client.close()

        with suppress(KeyError, TypeError):
            _log.error("This is a trackmania.io error")
            raise TMIOException(search_result["error"])

        if len(search_result) == 0:
            return None
        elif len(search_result) == 1:
            return PlayerSearchResult._from_dict(search_result[0])
        else:
            players = list()
            for player in search_result:
                players.append(PlayerSearchResult._from_dict(player))

            return players

    @staticmethod
    async def get_id(username: str) -> str:
        """
        .. versionadded :: 0.1.0

        Gets a player's id from the given username

        Parameters
        ----------
        username : str
            The player's username to get the ID for.

        Returns
        -------
        str
            The player's id.
        """
        _log.debug(f"Getting {username}'s id")

        cache_client = redis.Redis(
            host=Client.REDIS_HOST,
            port=Client.REDIS_PORT,
            db=Client.REDIS_DB,
            password=Client.REDIS_PASSWORD,
        )

        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            if cache_client.exists(f"{username.lower()}:id"):
                _log.debug(f"{username}'s id found in cache")
                return cache_client.get(f"{username.lower()}:id").decode("utf-8")

        players = await Player.search(username)

        if players is None:
            with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
                _log.debug(f"Caching {username.lower()} id as None")
                cache_client.set(f"{username.lower()}:id", None)
        elif isinstance(players, PlayerSearchResult):
            with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
                _log.debug(f"Caching {username.lower()} id as {players.player_id}")
                cache_client.set(f"{username.lower()}:id", players.player_id)
            return players.player_id
        else:
            with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
                _log.debug(f"Caching {username.lower()} id as {players[0].player_id}")
                cache_client.set(f"{username.lower()}:id", players[0].player_id)
            return players[0].player_id

    @staticmethod
    async def get_username(player_id: str) -> str:
        """
        .. versionadded :: 0.1.0

        Gets a player's username from their player id

        Parameters
        ----------
        player_id : str
            The player id of the player

        Returns
        -------
        str
            The player's username
        """
        _log.debug(f"Getting the username for {player_id}")
        cache_client = redis.Redis(
            host=Client.REDIS_HOST,
            port=Client.REDIS_PORT,
            db=Client.REDIS_DB,
            password=Client.REDIS_PASSWORD,
        )

        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            if cache_client.exists(f"{player_id}:username"):
                _log.debug(f"{player_id}'s username found in cache")
                return json.loads(
                    cache_client.get(f"{player_id}:username").decode("utf-8")
                )

        player: Player = await Player.get(player_id)

        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            _log.debug(f"Caching {player_id}:username as {player.name}")
            cache_client.set(f"{player_id}:username", player.name)

        return player.name

    @staticmethod
    def _parse_player(player_data: Dict) -> Dict:
        """
        Parses the player data

        Parameters
        ----------
        player_data : :class:`Dict`
            The player data as a dictionary

        Returns
        -------
        :class:`Dict`
            The parsed player data formatted kwargs friendly for the :class:`Player` constructors
        """
        first_login = (
            datetime.strptime(player_data["timestamp"], "%Y-%m-%dT%H:%M:%S+00:00")
            if "timestamp" in player_data
            else None
        )

        last_club_tag_change = (
            datetime.strptime(
                player_data["clubtagtimestamp"], "%Y-%m-%dT%H:%M:%S+00:00"
            )
            if "clubtagtimestamp" in player_data
            else None
        )

        player_meta = (
            PlayerMetaInfo._from_dict(player_data["meta"])
            if "meta" in player_data
            else PlayerMetaInfo._from_dict(dict())
        )
        player_trophies = (
            PlayerTrophies._from_dict(player_data["trophies"], player_data["accountid"])
            if "trophies" in player_data
            else None
        )
        player_zone = (
            PlayerZone._parse_zones(
                player_data["trophies"]["zone"],
                player_data["trophies"]["zonepositions"],
            )
            if "trophies" in player_data and "zone" in player_data["trophies"]
            else None
        )

        player_id = (
            player_data["accountid"]
            if "accountid" in player_data
            else player_data["id"]
            if "id" in player_data
            else None
        )

        matchmaking = (
            PlayerMatchmaking._from_dict(player_data["matchmaking"], player_id)
            if "matchmaking" in player_data
            else [None, None]
        )

        club_tag = (
            player_data["clubtag"]
            if "clubtag" in player_data
            else player_data["tag"]
            if "tag" in player_data
            else None
        )
        name = (
            player_data["displayname"]
            if "displayname" in player_data
            else player_data["name"]
            if "name" in player_data
            else None
        )

        return {
            "club_tag": club_tag,
            "first_login": first_login,
            "name": name,
            "player_id": player_id,
            "last_club_tag_change": last_club_tag_change,
            "meta": player_meta,
            "trophies": player_trophies,
            "zone": player_zone,
            "m3v3_data": matchmaking[0],
            "royal_data": matchmaking[1],
        }
