from subprocess import ABOVE_NORMAL_PRIORITY_CLASS
from types import NoneType
from typing import Dict, List
from datetime import datetime
import logging
from contextlib import suppress
import json

import redis

from .api import APIClient
from .errors import InvalidTrophyNumber, InvalidIDError, InvalidUsernameError
from .constants import TMIO
from .config import Client

_log = logging.getLogger(__name__)

__all__ = (
    "PlayerMetaInfo",
    "PlayerTrophies",
    "PlayerZone",
    "PlayerMatchmaking",
    "Player",
)


class PlayerMetaInfo:
    """
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
    def from_dict(cls, meta_data: Dict):
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


class PlayerTrophies:
    """
    Represents Player Trophies

    Parameters
    ----------
    echelon : int
        The trophy echelon of the player.
    last_change : str
        The date of the last change of the player's self.
    points : ints: int
        The number of points of the player.
    trophies : :class:`List[int]`
        The number of trophies of the player.
    player_id : str | :class:`NoneType`, optional
        The Trackmania ID of the player
    """

    def __init__(
        self,
        echelon: int,
        last_change: datetime,
        points: int,
        trophies: List[int],
        player_id: str | NoneType = None,
    ):
        """Constructor for the class."""
        self.echelon = echelon
        self._last_change = last_change
        self.points = points
        self.trophies = trophies
        self._player_id = player_id

    @classmethod
    def from_dict(cls, raw_trophy_data: Dict, player_id: str):
        """
        Creates a :class:`PlayerTrophies` object from the given dictionary.

        Parameters
        ----------
        raw_trophy_data : :class:`Dict`
            The raw trophy data to parse.
        player_id : str
            The player ID to set.
        Returns
        -------
        :class:`PlayerTrophies`
            The parsed trophy data.
        """
        _log.debug(f"Creating a PlayerTrophies class from the given dictionary.")

        return cls(
            echelon=raw_trophy_data["echelon"],
            last_change=datetime.strptime(
                raw_trophy_data["timestamp"], "%Y-%m-%dT%H:%M:%S+00:00"
            ),
            points=raw_trophy_data["points"],
            trophies=raw_trophy_data["counts"],
            player_id=player_id,
        )

    @property
    def last_change(self):
        """Last change property."""
        return self._last_change

    @property
    def player_id(self):
        """player_id property"""
        return self._player_id

    def set_id(self, player_id: str):
        """Setter for player_id"""
        self._player_id = player_id

    def trophy(self, number: int) -> int:
        """
        Returns the trophies by tier.

        Parameters
        ----------
        number : int
            The trophy number, from 1 (T1) to 9 (T9).
        Returns
        -------
        int
            the number of trophies for that specific tier.
        """
        _log.debug(f"Returning trophy T{number} for player {self.player_id}")

        if number > 9 or number < 1:
            raise InvalidTrophyNumber(
                "Trophy Number cannot be less than 1 or greater than 9"
            )

        return self.trophies[number - 1]

    def score(self) -> int:
        """Returns the trophy score of the player."""
        return (
            0
            + self.trophy(1) * 1
            + self.trophy(2) * 10
            + self.trophy(3) * 100
            + self.trophy(4) * 1_000
            + self.trophy(5) * 10_000
            + self.trophy(6) * 100_000
            + self.trophy(7) * 1_000_000
            + self.trophy(8) * 10_000_000
        )

    # async def trophy_history function
    async def history(self, page: int = 0) -> Dict:
        """
        Retrieves Trophy Gain and Loss history of a player.

        Parameters
        ----------
        page : int, optional
            page number of trophy history, by default 0
        Returns
        -------
        :class:`Dict`
            Trophy history data.
        Raises
        ------
        InvalidIDError
            If an ID has not been set for the object.
        InvalidIDError
            If an invalid id has been set for the object.
        """
        api_client = APIClient()

        if self.player_id is None:
            raise InvalidIDError("ID Has not been set for the Object")

        _log.info(
            f"Sending GET request to {TMIO.build([TMIO.TABS.PLAYER, self.player_id, TMIO.TABS.TROPHIES, page])}"
        )
        history = await api_client.get(
            TMIO.build([TMIO.TABS.PLAYER, self.player_id, TMIO.TABS.TROPHIES, page])
        )

        await api_client.close()
        return history["gains"]


class PlayerZone:
    """
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
        player_zone_list: List = []
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


class PlayerMatchmaking:
    """
    Class that represents the player matchmaking details

    Parameters
    ----------
    type : str
        The type of matchmaking, either "3v3" or "Royal"
    type_id : int
        The type of matchmaking as 0 or 1, 0 for "3v3" and 1 for "Royal"
    progression : int
        The progression of the player's score in matchmaking
    rank : int
        The rank of the player in matchmaking
    score : int
        The score of the player in matchmaking
    division : int
        The division of the player in matchmaking
    division_str : str: str
        The division of the player in matchmaking as a string
    min_points : ints: int
        The points required to reach the current division.
    max_points : ints: int
        The points required to move up the rank.
    """

    def __init__(
        self,
        matchmaking_type: str,
        type_id: int,
        progression: int,
        rank: int,
        score: int,
        division: int,
        min_points: int,
        max_points: int,
    ):
        """Constructor for the class."""
        MATCHMAKING_STRING = {
            1: "Bronze 3",
            2: "Bronze 2",
            3: "Bronze 1",
            4: "Silver 3",
            5: "Silver 2",
            6: "Silver 1",
            7: "Gold 3",
            8: "Gold 2",
            9: "Gold 1",
            10: "Master 3",
            11: "Master 2",
            12: "Master 1",
            13: "Trackmaster",
        }

        self.matchmaking_type = matchmaking_type
        self.type_id = type_id
        self.rank = rank
        self.score = score
        self.progression = progression
        self.division = division
        self.division_str = MATCHMAKING_STRING[division]
        self._min_points = min_points
        self._max_points = 1 if max_points == 0 else max_points

        try:
            self.progress = round(
                (score - min_points) / (max_points - min_points) * 100, 2
            )
        except ZeroDivisionError:
            self.progress = 0

    @staticmethod
    def from_dict(mm_data: Dict):
        """
        Parses the matchmaking data of the player and returns 2 :class:`PlayerMatchmaking` objects.
            One for 3v3 Matchmaking and the other for Royal matchmaking.
        Parameters
        ----------
        mm_data : :class:`List[Dict]`
            The matchmaking data.
        Returns
        -------
        :class:`List[PlayerMatchmaking]`
            The list of matchmaking data, one for 3v3 and other other one for royal.
        """
        matchmaking_data = []

        if len(mm_data) == 0:
            matchmaking_data.extend([None, None])
        elif len(mm_data) == 1:
            matchmaking_data.extend([PlayerMatchmaking.__parse_3v3(mm_data[0]), None])
        else:
            matchmaking_data.extend(
                [
                    PlayerMatchmaking.__parse_3v3(mm_data[0]),
                    PlayerMatchmaking.__parse_3v3(mm_data[1]),
                ]
            )

        return matchmaking_data

    @classmethod
    def __parse_3v3(cls, data: Dict):
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

        return cls(
            typename, typeid, progression, rank, score, division, min_points, max_points
        )

    @property
    def min_points(self):
        """min points property"""
        return self._min_points

    @property
    def max_points(self):
        """max points property"""
        return self._max_points


class PlayerSearchResult:
    """
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
    def from_dict(cls, player_data: Dict):
        zone = PlayerZone._parse_zones(player_data["player"]["zone"], [0, 0, 0, 0, 0])
        club_tag = (
            player_data["player"]["club_tag"]
            if "club_tag" in player_data["player"]
            else None
        )
        name = player_data["player"]["name"]
        player_id = player_data["player"]["id"]
        matchmaking = PlayerMatchmaking.from_dict(player_data["matchmaking"])

        return cls(club_tag, name, player_id, zone, matchmaking[0], matchmaking[1])


class Player:
    """
    Represents a Player in Trackmania

    Parameters
    ----------
    club_tag : str | None.
        The club tag of the player, `NoneType` if the player is not in a club.
    first_login : str
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
        first_login: str,
        player_id: str,
        last_club_tag_change: str,
        meta: PlayerMetaInfo,
        name: str,
        trophies: PlayerTrophies = None,
        zone: List[PlayerZone] = None,
        m3v3_data: PlayerMatchmaking = None,
        royal_data: PlayerMatchmaking = None,
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
                player_data = cache_client.get(f"player:{player_id}")
                player_data = json.loads(player_data)
                return cls(
                    **Player._parse_player(cache_client.get(f"player:{player_id}"))
                )

        api_client = APIClient()
        _log.info(f"Sending GET request to {TMIO.build([TMIO.TABS.PLAYER, player_id])}")
        player_data = await api_client.get(TMIO.build([TMIO.TABS.PLAYER, player_id]))
        await api_client.close()

        # add caching

        return cls(**Player._parse_player(player_data))

    @staticmethod
    async def search(
        username: str,
    ) -> None | PlayerSearchResult | List[PlayerSearchResult]:
        """
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
        api_client = APIClient()
        _log.info(
            f"Sending GET request to {TMIO.build([TMIO.TABS.PLAYERS])}"
            + f"find?search={username}"
        )
        search_result = await api_client.get(
            TMIO.build([TMIO.TABS.PLAYERS]) + f"find?search={username}"
        )
        await api_client.close()

        if len(search_result) == 0:
            return None
        elif len(search_result) == 1:
            return PlayerSearchResult.from_dict(search_result[0])
        else:
            players = []
            for player in search_result:
                players.append(PlayerSearchResult.from_dict(player))

            return players

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
        first_login = datetime.strptime(
            player_data["timestamp"], "%Y-%m-%dT%H:%M:%S+00:00"
        )
        last_club_tag_change = (
            datetime.strptime(
                player_data["clubtagtimestamp"], "%Y-%m-%dT%H:%M:%S+00:00"
            )
            if "clubtagtimestamp" in player_data
            else None
        )

        player_meta = PlayerMetaInfo.from_dict(player_data["meta"])
        player_trophies = PlayerTrophies.from_dict(
            player_data["trophies"], player_data["accountid"]
        )
        player_zone = PlayerZone._parse_zones(
            player_data["trophies"]["zone"], player_data["trophies"]["zonepositions"]
        )
        matchmaking = PlayerMatchmaking.from_dict(player_data["matchmaking"])

        return {
            "club_tag": player_data["clubtag"] if "clubtag" in player_data else None,
            "first_login": first_login,
            "name": player_data["displayname"],
            "player_id": player_data["accountid"],
            "last_club_tag_change": last_club_tag_change,
            "meta": player_meta,
            "trophies": player_trophies,
            "zone": player_zone,
            "m3v3_data": matchmaking[0],
            "royal_data": matchmaking[1],
        }
