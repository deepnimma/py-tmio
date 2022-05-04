import logging
from contextlib import suppress
from datetime import datetime
from pickletools import TAKEN_FROM_ARGUMENT1

from typing_extensions import Self

from ._util import _regex_it
from .api import _APIClient
from .config import get_from_cache, set_in_cache
from .constants import _TMIO
from .errors import TMIOException
from .player import Player
from .tmmap import TMMap

_log = logging.getLogger(__name__)

__all__ = (
    "ClubMember",
    "ClubActivity",
    "Club",
)


class ClubMember:
    """
    .. versionadded :: 0.5

    Represents a member of a club.

    Parameters
    ----------
    name : str
        The name of the player.
    tag : str | None
        The club tab of the player.
    player_id : str
        The ID of the player.
    join_time : datetime
        When the player joined the club.
    role : str
        The role of the player inside the club
    vip : bool
        Whether the player is a VIP.
    """

    def __init__(
        self,
        name: str,
        tag: str | None,
        player_id: str,
        join_time: datetime,
        role: str,
        vip: bool,
    ):
        self.name = name
        self.tag = tag
        self.player_id = player_id
        self.join_time = join_time
        self.role = role
        self.vip = vip

    @classmethod
    def _from_dict(cls: Self, raw_data: dict) -> Self:
        _log.debug("Creating a ClubMember class from the given dictionary")
        name = _regex_it(raw_data["player"].get("name"))
        tag = _regex_it(raw_data["player"].get("tag", None))
        player_id = raw_data["player"].get("id")
        join_time = datetime.utcfromtimestamp(raw_data.get("joinTime"))
        role = raw_data.get("role")
        vip = raw_data.get("vip")

        args = [
            name,
            tag,
            player_id,
            join_time,
            role,
            vip,
        ]

        return cls(*args)

    async def player(self) -> Player:
        """
        .. versionadded :: 0.5

        Gets the player who is this specific club member.
        (IDK wtf to put here xD)

        Returns
        -------
        :class:`Player`
            The player who is the club member.

        Raises
        ------
        :class:`TMIOException`
            If there is a problem with the TMIO API.
        """
        return await Player.get_player(self.player_id)


class ClubActivity:
    """
    .. versionadded :: 0.5

    Represents an activity of the club.

    Parameters
    ----------
    name : str
        The name of the activity.
    type : str
        What type of activity it is.
    activity_id : int
        The activity's ID.
    target_activity_id : int
        The activity's target ID.
    position : int
        The position of the activity within the club.
    public : bool
        Whether the activity is public or club-member only.
    media : str
        The media of the activity.
    password : bool
        Whether the activity is password-protected.
    """

    def __init__(
        self,
        name: str,
        type: str,
        activity_id: int,
        target_activity_id: int,
        position: int,
        public: bool,
        media: str,
        password: bool,
    ):
        self.name = name
        self.type = type
        self.activity_id = activity_id
        self.target_activity_id = target_activity_id
        self.position = position
        self.public = public
        self.media = media
        self.password = password

    @classmethod
    def _from_dict(cls: Self, raw_data: dict) -> Self:
        _log.debug("Creating a ClubActivity class from the given dictionary")
        name = _regex_it(raw_data.get("name"))
        type = raw_data.get("type")
        activity_id = raw_data.get("activityid")
        target_activity_id = raw_data.get("targetactivityid", 0)
        position = raw_data.get("position")
        public = raw_data.get("public")
        media = raw_data.get("media")
        password = raw_data.get("password")

        args = [
            name,
            type,
            activity_id,
            target_activity_id,
            position,
            public,
            media,
            password,
        ]

        return cls(*args)


class Club:
    """
    Represents a Club in Trackmania 2020.

    Parameters
    ----------
    background : str
        The club's background url.
    created_at : datetime
        The club's created date.
    decal : str
        The club decal URL
    description : str
        The club's description
    featured : bool
        Whether the club is featured or not.
    club_id : int
        The club's ID.
    logo : str
        The club's logo URL.
    member_count : int
        The club's member count.
    name : str
        The club's name.
    popularity : int
        The club popularity level
    state : str
        The club's state.
        Is either Private or Public.
    tag : str
        The club tag
    """

    def __init__(
        self,
        background: str,
        created_at: datetime,
        decal: str,
        description: str,
        featured: bool,
        club_id: int,
        logo: str,
        member_count: int,
        name: str,
        popularity: int,
        state: str,
        tag: str | None,
        creator_id: str,
    ):
        self.background = background
        self.created_at = created_at
        self.decal = decal
        self.description = description
        self.featured = featured
        self.club_id = club_id
        self.logo = logo
        self.member_count = member_count
        self.name = name
        self.popularity = popularity
        self.state = state
        self.tag = tag
        self.creator_id = creator_id

    @classmethod
    def _from_dict(cls: Self, raw_data: dict) -> Self:
        _log.debug("Creating a Club class from the given dictionary.")
        background = raw_data.get("backgroundUrl", "")
        created_at = datetime.utcfromtimestamp(raw_data.get("creationTimestamp", 0))
        decal = raw_data.get("decalUrl")
        description = raw_data.get("description")
        featured = raw_data.get("featured")
        club_id = raw_data.get("id", 0)
        logo = raw_data.get("logoUrl")
        member_count = raw_data.get("membercount", 0)
        name = _regex_it(raw_data.get("name"))
        popularity = raw_data.get("popularityLevel")
        state = raw_data.get("state")
        tag = _regex_it(raw_data.get("tag", None))
        creator_id = raw_data["creatorplayer"]["id"]

        args = [
            background,
            created_at,
            decal,
            description,
            featured,
            club_id,
            logo,
            member_count,
            name,
            popularity,
            state,
            tag,
            creator_id,
        ]

        return cls(*args)

    @classmethod
    async def get_club(cls: Self, club_id: int) -> Self | None:
        """
        .. versionadded :: 0.5

        Gets a club based on its club id.
        Returns None if the `club_id` is 0

        Parameters
        ----------
        club_id : int
            The club's id.

        Returns
        -------
        :class:`Club` | None
            Returns a `Club` class if a club exists with the given class id. Otherwise returns None.

        Raises
        ------
        :class:`TMIOException`
            If the club doesn't exist or if an unexpected error occurs on TMIO's side.
        """
        if club_id == 0:
            return None

        club_data = get_from_cache(f"club:{club_id}")
        if club_data is not None:
            return cls._from_dict(club_data)

        api_client = _APIClient()
        club_data = await api_client.get(_TMIO.build([_TMIO.TABS.CLUB, club_id]))
        await api_client.close()

        with suppress(KeyError, TypeError):
            raise TMIOException(club_data["error"])

        return cls._from_dict(club_data)

    @classmethod
    async def list_clubs(cls: Self, page: int = 0) -> list[Self]:
        """
        .. versionadded :: 0.5

        Lists all the popular clubs.

        Parameters
        ----------
        page : int, optional
            The page bumber, by default 0

        Returns
        -------
        :class:`list[Club]`
            The list of clubs on that specific page.
        """
        clubs = []
        club_data = get_from_cache(f"clubs:{page}")
        if club_data is not None:
            for club in club_data.get("clubs", []):
                clubs.append(cls._from_dict(club))

            return clubs

        api_client = _APIClient()
        club_data = await api_client.get(
            _TMIO.build([_TMIO.TABS.CLUBS, page]) + "?sort=popularity"
        )
        await api_client.close()

        set_in_cache(f"clubs:{page}", club_data, ex=43200)

        for club in club_data.get("clubs", []):
            clubs.append(cls._from_dict(club))

        return clubs

    async def get_activities(self: Self, page: int = 0) -> list[ClubActivity]:
        """
        .. versionadded :: 0.5

        Gets the activities of the club.

        Parameters
        ----------
        page : int
            The page number, by default 0

        Returns
        -------
        :class:`list[ClubActivity]`
            The list of activities of the club.
        """
        club_activities = []
        all_activities = get_from_cache(f"club_activities:{self.club_id}:{page}")

        if all_activities is not None:
            for activity in all_activities:
                club_activities.append(ClubActivity._from_dict(activity))

            return club_activities

        api_client = _APIClient()
        all_activities = await api_client.get(
            _TMIO.build([_TMIO.TABS.CLUB, self.club_id, _TMIO.TABS.ACTIVITIES, page])
        )
        await api_client.close()

        with suppress(KeyError, TypeError):
            raise TMIOException(all_activities["error"])

        for activity in all_activities.get("activities", []):
            club_activities.append(ClubActivity._from_dict(activity))

        return club_activities

    async def get_members(self: Self, page: int = 0) -> list[ClubMember]:
        """
        .. versionadded :: 0.5

        Gets the members of the club.

        Parameters
        ----------
        page : int, optional
            The page number, by default 0

        Returns
        -------
        :class:`list[Player]`
            The list of members of the club.
        """
        player_list = []
        club_members = get_from_cache(f"club_members:{self.club_id}:{page}")

        if club_members is not None:
            for member in club_members.get("members", []):
                player_list.append(ClubMember._from_dict(member))

            return player_list

        api_client = _APIClient()
        club_members = await api_client.get(
            _TMIO.build([_TMIO.TABS.CLUB, self.club_id, _TMIO.TABS.MEMBERS, page])
        )
        await api_client.close()

        for member in club_members.get("members", []):
            player_list.append(ClubMember._from_dict(member))

        return player_list

    async def creator(self) -> Player:
        """
        .. versionadded :: 0.5

        Gets the creator of the club.

        Returns
        -------
        :class:`Player`
            The creator of the club.
        """
        return await Player.get_player(self.creator_id)
