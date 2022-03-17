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
    """Represents Player Meta Data, which inclues YT, Twitch, Twitter or TMIO Vanity Link

    :param display_url: The URL to the player's profile
    :type display_url: str
    :param in_nadeo: Whether the player is in Nadeo
    :type in_nadeo: bool
    :param in_tmgl: Whether the player is in TMGL
    :type in_tmgl: bool
    :param in_tmio_dev_team: Whether the player is in TMIO Dev Team
    :type in_tmio_dev_team: bool
    :param in_tmwc21: Whether the player is in TMWC21
    :type in_tmwc21: bool
    :param is_sponsor: Whether the player is a sponsor
    :type is_sponsor: bool
    :param sponsor_level: The sponsor level of the player
    :type sponsor_level: int | None
    :param twitch: The Twitch URL of the player, :class:`NoneType` if the player has no Twitch
    :type twitch: str | None
    :param twitter: The Twitter URL of the player, :class:`NoneType` if the player has no Twitter
    :type twitter: str | None
    :param youtube: The YouTube URL of the player, :class:`NoneType` if the player has no YouTube
    :type youtube: str | None
    :param vanity: The TMIO Vanity URL of the player, :class:`NoneType` if the player has no TMIO Vanity URL
    :type vanity: str | None
    """

    def __init__(
        self,
        display_url: str,
        in_nadeo: bool,
        in_tmgl: bool,
        in_tmio_dev_team: bool,
        in_tmwc21: bool,
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
        self.in_tmwc21 = in_tmwc21
        self.is_sponsor = is_sponsor
        self.sponsor_level = sponsor_level
        self.twitch = twitch
        self.twitter = twitter
        self.youtube = youtube
        self.vanity = vanity


class PlayerTrophies:
    """Represents Player Trophies

    :param echelon: The trophy echelon of the player.
    :type echelon: int
    :param last_change: The date of the last change of the player's self.
    :type last_change: str
    :param points: The number of points of the player.
    :type points: int
    :param trophies: The number of trophies of the player.
    :type trophies: :class:`List`[int]
    :param player_id: The Trackmania ID of the player
    :type player_id: str, optional
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
        """
        Constructor for the class.
        """
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

        :param page: Page number of trophy history, defaults to 0
        :type page: int, optional
        :raises :class:`InvalidIDError`: If an ID has not been set for the object or an invalid id has been given to the player object.
        :return: Trophy history data.
        :rtype: :class:`Dict`
        """
        api_client = APIClient()

        if self.player_id is None:
            raise InvalidIDError("ID Has not been set for the Object")

        history = await api_client.get(
            TMIO.build([TMIO.tabs.player, self.player_id, TMIO.tabs.trophies, page])
        )

        await api_client.close()

        try:
            return history["gains"]
        except KeyError:
            raise InvalidIDError(f"Player ID {self.player_id} does not exist")

    def set_id(self, player_id: str):
        """
        Sets the ID of the player.

        :param player_id: The Trackmania ID of the player.
        :type player_id: str
        """
        self.player_id = player_id

    def trophy(self, number: int) -> int:
        """
        Returns the trophies by tier.

        :param number: The trophy number, from 1 (T1) to 9 (T9).
        :type number: int
        :raises :class:`InvalidTrophyNumber`: If the number is not between 1 and 9.
        :return: the number of trophies for that specific tier.
        :rtype: int
        """

        if number > 9 or number < 1:
            raise InvalidTrophyNumber(
                "Trophy Number cannot be less than 1 or greater than 9"
            )

        return self.trophies[number - 1]

    def score(self) -> int:
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
    """
    Class that represents the player zone

    :param flag: The flag of the zone
    :type flag: str
    :param zone: The zone name
    :type zone: str
    :param rank: The rank of the player in the zone
    :type rank: int
    """

    def __init__(self, flag: str, zone: str, rank: int):
        """Constructor method."""
        self.flag = flag
        self.zone = zone
        self.rank = rank


class PlayerMatchmaking:
    """Class that represents the player matchmaking details

    :param type: The type of matchmaking, either "3v3" or "Royal"
    :type type: str
    :param type_id: The type of matchmaking as 0 or 1, 0 for "3v3" and 1 for "Royal"
    :type type_id: int
    :param progression: The progression of the player's score in matchmaking
    :type progression: int
    :param rank: The rank of the player in matchmaking
    :type rank: int
    :param score: The score of the player in matchmaking
    :type score: int
    :param division: The division of the player in matchmaking
    :type division: int
    :param division_str: The division of the player in matchmaking as a string
    :type division_str: str
    :param min_points: The points required to reach the current division.
    :type min_points: int
    :param max_points: The points required to move up the rank.
    :type max_points: int
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
        """
        Constructor for the class.
        """
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
    """Represents a Player in Trackmania

    :param club_tag: The club tag of the player, :class:`NoneType` if the player is not in a club.
    :type club_tag: str | None.
    :param first_login: The date of the first login of the player.
    :type first_login: str
    :param player_id: The Trackmania ID of the player.
    :type player_id: str
    :param last_club_tag_change: The date of the last club tag change of the player.
    :type last_club_tag_change: str
    :param login: Login of the player.
    :type login: str
    :param meta: Meta data of the player.
    :type meta: :class:`PlayerMetaInfo`.
    :param name: Name of the player.
    :type name: str
    :param trophies: The trophies of the player.
    :type trophies: :class:`PlayerTrophies`, optional
    :param zone: The zone of the player as a list.
    :type zone: :class:`List[PlayerZone]`, optional
    :param m3v3_data: The 3v3 data of the player.
    :type m3v3_data: :class:`PlayerMatchmaking`, optional
    :param royal_data: The royal data of the player.
    :type royal_data: :class:`PlayerMatchmaking`, optional
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
        """
        Constructor of the class.
        """
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
        """
        String representation of the class.
        """
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
    """Represents 1 Player from a Search Result

    :param club_tag: The club tag of the player, :class:`NoneType` if the player is not in a club.
    :type club_tag: str | None.
    :param name: Name of the player.
    :type name: str
    :param player_id: The Trackmania ID of the player.
    :type player_id: str
    :param zone: The zone of the player as a list.
    :type zone: :class:`List[PlayerZone]`, optional
    :param threes: The 3v3 data of the player.
    :type threes: :class:`PlayerMatchmaking`, optional
    :param royals: The royal data of the player.
    :type royals: :class:`PlayerMatchmaking`, optional
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
