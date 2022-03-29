# pylint: disable=too-many-arguments,too-few-public-methods,too-many-instance-attributes

from typing import Dict, List

from ..api import APIClient
from ..constants import TMIO
from ..errors import InvalidIDError, InvalidTrophyNumber

__all__ = (
    "PlayerMetaInfo",
    "PlayerTrophies",
    "PlayerZone",
    "PlayerMatchmaking",
    "Player",
    "PlayerSearchResult",
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

    Returns
    -------

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
    player_id : str, optional
        The Trackmania ID of the player

    """

    # Add a last_change str to datetime converter

    def __init__(
        self,
        echelon: int,
        last_change: str,
        points: int,
        trophies: List[int],
        player_id: str = None,
    ):
        """Constructor for the class."""
        self.echelon = echelon
        self._last_change = last_change
        self.points = points
        self.trophies = trophies
        self.player_id = player_id

    @property
    def last_change(self):
        """Last change property."""
        return self._last_change

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

        history = await api_client.get(
            TMIO.build([TMIO.TABS.PLAYER, self.player_id, TMIO.TABS.TROPHIES, page])
        )

        await api_client.close()

        try:
            return history["gains"]
        except KeyError:
            raise InvalidIDError(f"Player ID {self.player_id} does not exist")

    def set_id(self, player_id: str):
        """Sets the ID of the player.

        Parameters
        ----------
        player_id : str
            The Trackmania ID of the player.
        """
        self.player_id = player_id

    def trophy(self, number: int) -> int:
        """Returns the trophies by tier.

        Parameters
        ----------
        number : int
            The trophy number, from 1 (T1) to 9 (T9).

        Returns
        -------
        int
            the number of trophies for that specific tier.
        """

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


class PlayerZone:
    """Class that represents the player zone

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
        matchmaking_string = {
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
        self.division_str = matchmaking_string[division]
        self._min_points = min_points
        self._max_points = 1 if max_points == 0 else max_points

        try:
            self.progress = round(
                (score - min_points) / (max_points - min_points) * 100, 2
            )
        except ZeroDivisionError:
            self.progress = 0

    @property
    def min_points(self):
        """min points property"""
        return self._min_points

    @property
    def max_points(self):
        """max points property"""
        return self._max_points


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
        login: str,
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
        self.login = login
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

    Returns
    -------

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
        """Constructor method."""
        self.club_tag = club_tag
        self.name = name
        self.player_id = player_id
        self.zone = zone
        self.threes = threes
        self.royal = royal
