import logging
from contextlib import suppress
from datetime import datetime

from typing_extensions import Self

from ._util import _regex_it
from .api import _APIClient
from .config import get_from_cache, set_in_cache
from .constants import _TMIO
from .errors import TMIOException
from .player import Player
from .tmmap import TMMap

_log = logging.getLogger(__name__)


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
    vertical : str
        The club vertical background URL.
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
        name = raw_data.get("name")
        popularity = raw_data.get("popularityLevel")
        state = raw_data.get("state")
        tag = _regex_it(raw_data.get("tag"), None)
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

    async def creator(self) -> Player:
        """
        Gets the creator of the club.

        Returns
        -------
        :class:`Player`
            The creator of the club.
        """
        return await Player.get_player(self.creator_id)
