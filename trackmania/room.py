import logging
from contextlib import suppress

from typing_extensions import Self

from trackmania.errors import TMIOException

from ._util import _regex_it
from .api import _APIClient
from .club import Club
from .config import get_from_cache, set_in_cache
from .constants import _TMIO
from .tmmap import TMMap

_log = logging.getLogger(__name__)

__all__ = (
    "RoomSearchResult",
    "Room",
)


class RoomSearchResult:
    """
    .. versionadded :: 0.5

    Represents a SearchResult from the `Room.search()` and `Room.popular_rooms()` command

    Parameters
    ----------
    name : str
        The name of the room.
    room_id : int
        The id of the room.
    club_id : int
        The club id of the club the room belongs to.
    nadeo : bool
        Whether nadeo owns this room.
    player_count : int
        The current number of players currently online and in the room.
    max_player_count : int
        The number of players allowed to join the room.
    """

    def __init__(
        self,
        name: str,
        room_id: int,
        club_id: int,
        nadeo: bool,
        player_count: int,
        max_player_count: int,
    ):
        self.name = name
        self.room_id = room_id
        self.club_id = club_id
        self.nadeo = nadeo
        self.player_count = player_count
        self.max_player_count = max_player_count

    @classmethod
    def _from_dict(cls: Self, raw_data: dict) -> Self:
        name = _regex_it(raw_data.get("name"))
        room_id = raw_data.get("id")
        club_id = raw_data.get("clubid")
        nadeo = raw_data.get("nadeo")
        player_count = raw_data.get("playercount")
        max_player_count = raw_data.get("maxplayercount")

        args = [name, room_id, club_id, nadeo, player_count, max_player_count]

        return cls(*args)

    async def club(self: Self) -> Club:
        """
        .. versionadded :: 0.5

        Returns the club the room belongs to.

        Returns
        -------
        :class:`Club`
            The club the room belongs to.
        """
        return await Club.get_club(self.club_id)

    async def room(self: Self):
        """
        .. versionadded :: 0.5

        Returns the Room itself with its full data from the api.

        Returns
        -------
        :class:`Room`
            The room itself.
        """
        return await Room.get_room(self.club_id, self.room_id)


class Room:
    """
    .. versionadded :: 0.5

    Represents a Club Room in trackmania 2020.

    Parameters
    ----------
    room_id : int
        The id of the room.
    image_url : str
        The url of the image of the room.
    nadeo : bool
        Whether the room is hosted in a cloud server. True only if it's by nadeo.
    login : str | None
        The login of the room. None if the room is in the cloud.
    max_players_count : int
        The maximum number of players allowed to join the room.
    name : int
        The name of the room
    player_count : int
        The current number of players in the room.
    region : str
        Where the room is hosted.
        There can only be 2 locations:-
            1. `eu-west` - Europe West
            2. `ca-central` - Canada Central
    script : str
        The name of the script that is currently in use in the room.
    """

    def __init__(
        self,
        room_id: int,
        club_id: int,
        nadeo: bool,
        login: str | None,
        name: int,
        max_players_count: int,
        player_count: int,
        region: str,
        script: str,
        image_url: str,
        maps: list[TMMap],
    ):
        self.room_id = room_id
        self.club_id = club_id
        self.image_url = image_url
        self.nadeo = nadeo
        self.login = login
        self.name = name
        self.max_players_count = max_players_count
        self.player_count = player_count
        self.region = region
        self.script = script
        self._maps = maps

    @property
    def maps(self) -> list[TMMap]:
        """
        .. versionadded :: 0.5

        The maps of the room.

        Returns
        -------
        :class:`list[TMMap]`
            The maps of the room.
        """
        return self._maps

    @classmethod
    def _from_dict(cls: Self, raw_data: dict) -> Self:
        room_id = raw_data.get("id", 0)
        club_id = raw_data.get("clubid")
        nadeo = raw_data.get("nadeo")
        login = raw_data.get("login")
        name = _regex_it(raw_data.get("name"))
        max_players_count = raw_data.get("playermax", 0)
        player_count = raw_data.get("playercount")
        region = raw_data.get("region", "")
        script = raw_data.get("script")
        image_url = raw_data.get("mediaurl")
        maps = []

        for map in raw_data.get("maps", []):
            maps.append(TMMap._from_dict(map))

        args = [
            room_id,
            club_id,
            nadeo,
            login,
            name,
            max_players_count,
            player_count,
            region,
            script,
            image_url,
            maps,
        ]

        return cls(*args)

    @classmethod
    async def get_room(cls: Self, club_id: int, room_id: int) -> Self:
        """
        .. versionadded :: 0.5

        Gets a room using it's club and room id.

        Parameters
        ----------
        club_id : int
            The club to which the room belongs to
        room_id : int
            The room's id.

        Returns
        -------
        :class:`Room`
            The room.
        """
        club_data = get_from_cache(f"room:{club_id}:{room_id}")
        if club_data is not None:
            return cls._from_dict(club_data)

        api_client = _APIClient()
        club_data = await api_client.get(
            _TMIO.build([_TMIO.TABS.ROOM, club_id, room_id])
        )
        await api_client.close()

        with suppress(KeyError, TypeError):
            raise TMIOException(club_data["error"])

        set_in_cache(f"room:{club_id}:{room_id}", club_data)

        return cls._from_dict(club_data)

    @staticmethod
    async def popular_rooms(page: int = 0) -> list[RoomSearchResult]:
        """
        .. versionadded :: 0.5

        Gets the popular club rooms.
        Popular club rooms are based on the number of players currently playing on the server.

        Parameters
        ----------
        page : int, optional
            The page of the popular rooms data, by default 0

        Returns
        -------
        :class:`list[RoomSearchResult]`
            The popular rooms.
        """
        popular_rooms = []
        popular_rooms_data = get_from_cache(f"popular_rooms:{page}")

        if popular_rooms_data is not None:
            for room in popular_rooms_data.get("rooms", []):
                popular_rooms.append(RoomSearchResult._from_dict(room))

            return popular_rooms

        api_client = _APIClient()
        popular_rooms_data = await api_client.get(_TMIO.build([_TMIO.TABS.ROOMS, page]))
        await api_client.close()

        with suppress(KeyError, TypeError):
            raise TMIOException(popular_rooms_data["error"])

        set_in_cache(f"popular_rooms:{page}", popular_rooms_data)

        for room in popular_rooms_data.get("rooms", []):
            popular_rooms.append(RoomSearchResult._from_dict(room))

        return popular_rooms

    async def club(self: Self) -> Club:
        """
        .. versionadded :: 0.5

        Gets the club the room belongs to.

        Returns
        -------
        :class:`Club`
            The club the room belongs to.
        """
        return await Club.get_club(self.club_id)
