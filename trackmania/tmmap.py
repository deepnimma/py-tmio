import json
import logging
from contextlib import suppress
from datetime import datetime
from typing import Dict, List

import redis
from typing_extensions import Self

from trackmania.api import _APIClient

from ._util import _regex_it
from .api import _APIClient
from .config import Client
from .constants import _TMIO
from .errors import TMIOException
from .player import Player

_log = logging.getLogger(__name__)

__all__ = (
    "MedalTimes",
    "Leaderboard",
    "TMMap",
)


class MedalTimes:
    """
    .. versionadded :: 0.3.0

    Represents a map's medal times

    Parameters
    ----------
    bronze : int
        The bronze medal time in ms
    silver : int
        The silver medal time in ms
    gold : int
        The gold medal time in ms
    author : int
        The author of the medal times
    bronze_string : str
        The bronze medal time in mm:ss:msmsms format
    silver_string : str
        The silver medal time in mm:ss:msmsms format
    gold_string : str
        The gold medal time in mm:ss:msmsms format
    author_string : str
        The author of the medal times in mm:ss:msmsms format
    """

    def __init__(self, bronze: int, silver: int, gold: int, author: int):
        self.bronze = bronze
        self.silver = silver
        self.gold = gold
        self.author = author
        self.bronze_string = self._parse_to_string(self.bronze)
        self.silver_string = self._parse_to_string(self.silver)
        self.gold_string = self._parse_to_string(self.gold)
        self.author_string = self._parse_to_string(self.author)

    def _parse_to_string(self, time: int) -> str:
        """
        Parses a medal time to a string in format `mm:ss:msms`

        Parameters
        ----------
        time : int
            The time to parse

        Returns
        -------
        str
            The time in mm:ss:msmsms format
        """
        _log.debug(f"Parsing {time} to string")

        sec, ms = divmod(time, 1000)
        min, sec = divmod(sec, 60)

        return "%01d:%02d.%03d" % (min, sec, ms)


class Leaderboard:
    """
    .. versionadded :: 0.3.0

    Represents the Map's Leaderboard

    Parameters
    ----------
    timestamp : :class:`datetime`
        The timestamp of the leaderboard was achieved
    ghost : str
        The url for the ghost download
    player_club_tag : str | None
        The player's club tag
    player_name : str
        The player's name
    player_id : str
        .. versionadded :: 0.3.4
        The player's id
    position : int
        The position of the player in the leaderboard
    time : int
        The time of the player in the leaderboard
    """

    def __init__(
        self,
        timestamp: datetime,
        ghost: str,
        player_club_tag: str | None,
        player_name: str | None,
        player_id: str | None,
        position: int,
        time: int,
    ):
        self.timestamp = timestamp
        self.ghost = ghost
        self.player_club_tag = player_club_tag
        self.player_name = player_name
        self.position = position
        self.time = time
        self.player_id = player_id

    @classmethod
    def _from_dict(cls: Self, raw: Dict) -> Self:
        _log.debug("Creating a Leaderboards class from given dictionary")

        if "player" in raw:
            player_id = raw.get("player").get("id")
            player_name = raw.get("player").get("name")
            player_club_tag = _regex_it(raw.get("player").get("tag", None))
        else:
            player_id = None
            player_name = None
            player_club_tag = None

        position = raw.get("position")
        time = raw.get("time")
        ghost = raw.get("url")
        timestamp = datetime.strptime(raw.get("timestamp"), "%Y-%m-%dT%H:%M:%S+00:00")

        return cls(
            timestamp=timestamp,
            ghost=ghost,
            player_club_tag=player_club_tag,
            player_name=player_name,
            position=position,
            time=time,
            player_id=player_id,
        )

    async def get_player(self) -> Player:
        """
        .. versionadded :: 0.3.4

        Gets the player who achieved the leaderboard.

        Returns
        -------
        :class:`Player`
            The player obj, None if the player_id does not exist.
        """
        if self.player_id is None:
            return None

        return await Player.get_player(self.player_id)


class TMMap:
    """
    .. versionadded :: 0.3.0

    Represents a Trackmania Map

    Parameters
    ----------
    author_id : str
        The author's player id
    environment : str
        The environment of the map
    exchange_id : str | None
        The exchange id of the map
    file_name : str
        The file name of the map
    map_id : str
        The map id of the map
    leaderboard : :class:`List[Leaderboard]` | None
        The leaderboard of the map
    medal_times : :class:`MedalTimes`
        The medal times of the map
    name : str
        The name of the map
    submitter_id : str
        The map's submitter's id
    thumbnail : str
        Link to the thumbnail of the map
    uid : str
        The uid of the map
    uploaded : :class:`datetime`
        The timestamp of when the map was uploaded
    url : str
        The url of the map download
    lb_loaded : bool
        Whether the leaderboard has been loaded
    """

    def __init__(
        self,
        author_id: str,
        author_name: str,
        environment: str,
        exchange_id: str | None,
        file_name: str,
        map_id: str,
        leaderboard: List[Leaderboard] | None,
        medal_time: MedalTimes,
        name: str,
        submitter_id: str,
        submitter_name: str,
        thumbnail: str,
        uid: str,
        uploaded: datetime,
        url: str,
    ):
        self.author_id = author_id
        self.author_name = author_name
        self.environment = environment
        self.exchange_id = exchange_id
        self.file_name = file_name
        self.map_id = map_id
        self.leaderboard = leaderboard
        self.medal_time = medal_time
        self.name = name
        self.submitter_id = submitter_id
        self.submitter_name = submitter_name
        self.thumbnail = thumbnail
        self.uid = uid
        self.uploaded = uploaded
        self.url = url
        self._offset = 0
        self.length = 100
        self._lb_loaded = False

    @property
    def offset(self):
        return self._offset

    @property
    def lb_loaded(self):
        return self._lb_loaded

    @classmethod
    def _from_dict(cls: Self, raw: Dict) -> Self:
        _log.debug("Creating a Map class from given dictionary")

        author_id = raw.get("author")
        author_name = _regex_it(raw.get("authorplayer").get("name"))
        environment = raw.get("collectionName")
        exchange_id = raw.get("exchangeid", None)
        file_name = raw.get("filename")
        map_id = raw.get("mapId")
        leaderboard = None
        medal_time = MedalTimes(
            raw.get("bronzeScore"),
            raw.get("silverScore"),
            raw.get("goldScore"),
            raw.get("authorScore"),
        )
        name = _regex_it(raw.get("name"))
        submitter_id = raw.get("submitter")
        submitter_name = raw.get("submitterplayer").get("name")
        thumbnail = raw.get("thumbnailUrl")
        uid = raw.get("mapUid")
        uploaded = datetime.strptime(raw.get("timestamp"), "%Y-%m-%dT%H:%M:%S+00:00")
        url = raw.get("fileUrl")

        return cls(
            author_id,
            author_name,
            environment,
            exchange_id,
            file_name,
            map_id,
            leaderboard,
            medal_time,
            name,
            submitter_id,
            submitter_name,
            thumbnail,
            uid,
            uploaded,
            url,
        )

    @classmethod
    async def get_map(cls: Self, map_uid: str) -> Self:
        """
        .. versionadded :: 0.3.0

        Gets the TM Map from the Map's UID

        Parameters
        ----------
        map_uid : str
            The map's UID
        """
        _log.debug(f"Getting the map with the UID {map_uid}")

        cache_client = Client._get_cache_client()

        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            if cache_client.exists(f"map:{map_uid}"):
                _log.debug(f"Map {map_uid} found in cache")
                return cls._from_dict(json.loads(cache_client.get(f"map:{map_uid}")))

        api_client = _APIClient()
        map_data = await api_client.get(_TMIO.build([_TMIO.TABS.MAP, map_uid]))
        await api_client.close()

        with suppress(KeyError, TypeError):

            raise TMIOException(map_data["error"])
        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            _log.debug(f"Caching map {map_uid}")
            cache_client.set(f"map:{map_uid}", json.dumps(map_data))

        return cls._from_dict(map_data)

    async def author(self) -> Player:
        """
        .. versionadded :: 0.3.0

        Returns the author as a player.

        Returns
        -------
        :class:`Player`
            The author as a :class:`Player` object
        """
        _log.debug(f"Getting the author of the map {self.uid}")
        return await Player.get_player(self.author_id)

    async def submitter(self) -> Player:
        """
        .. versionadded :: 0.3.0

        Returns the submitter as a player.

        Returns
        -------
        :class:`Player`
            The submitter as a :class:`Player` object
        """
        _log.debug(f"Getting the submitter of the map {self.uid}")
        return await Player.get_player(self.submitter_id)

    async def get_leaderboard(
        self, offset: int = 0, length: int = 100
    ) -> List[Leaderboard]:
        """
        .. versionadded :: 0.3.0

        Get's the leaderboard of a map.

        Parameters
        ----------
        offset : int, optional
            The offset of the leaderboard. Defaults to 0.
        length : int, optional
            How many leaderpositions to get. Should be between 1 and 100 both inclusive. by default 100

        Returns
        -------
        :class:`List[Leaderboard]`
            The leaderboard as a list of positions.

        Raises
        ------
        :class:`ValueError`
            If the length is not between 1 and 100.
        """
        if length < 1:
            raise ValueError("Length must be greater than 0")
        length = min(length, 100)

        _log.debug(
            f"Getting Leaderboard of the Map with Length {length} and offset {offset}"
        )

        cache_client = Client._get_cache_client()

        self._offset = offset
        self.length = length

        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            if cache_client.exists(
                f"leaderboard:{self.uid}:{self.offset}:{self.length}"
            ):
                _log.debug(
                    f"Leaderboard {self.uid}:{self.offset}:{self.length} found in cache"
                )
                leaderboards = []
                for lb in json.loads(
                    cache_client.get(
                        f"leaderboard:{self.uid}:{self.offset}:{self.length}"
                    ).decode("utf-8")
                )["tops"]:
                    leaderboards.append(Leaderboard._from_dict(lb))

                return leaderboards

        api_client = _APIClient()
        lb_data = await api_client.get(
            _TMIO.build([_TMIO.TABS.LEADERBOARD, _TMIO.TABS.MAP, self.uid])
            + f"?offset={self.offset}&length={self.length}"
        )
        await api_client.close()

        with suppress(KeyError, TypeError):

            raise TMIOException(lb_data["error"])
        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            _log.debug(f"Caching leaderboard {self.uid}:{self.offset}:{self.length}")
            cache_client.set(
                f"leaderboard:{self.uid}:{self.offset}:{self.length}",
                json.dumps(lb_data),
            )

        self._offset += self.length
        self._lb_loaded = True

        leaderboards = []
        for lb in lb_data["tops"]:
            leaderboards.append(Leaderboard._from_dict(lb))

        return leaderboards

    async def load_more_leaderboard(self, length: int = 100) -> List[Leaderboard]:
        """
        .. versionadded :: 0.3.0

        Gets more leaderboards for the map. If `get_leaderboards` wasn't used before then it just gets it from the start.

        Parameters
        ----------
        length : int, optional
            How many leaderboard positions to get, by default 100

        Returns
        -------
        :class:`List[Leaderboard]`
            The leaderboard positions.
        """
        cache_client = Client._get_cache_client()

        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            if cache_client.exists(
                f"leaderboard:{self.uid}:{self.offset}:{self.length}"
            ):
                _log.debug(
                    f"Leaderboard {self.uid}:{self.offset}:{self.length} found in cache"
                )
                leaderboards = []
                for lb in json.loads(
                    cache_client.get(
                        f"leaderboard:{self.uid}:{self.offset}:{self.length}"
                    ).decode("utf-8")
                )["tops"]:
                    leaderboards.append(Leaderboard._from_dict(lb))

                return leaderboards

        if not self._lb_loaded:
            _log.warn("Leaderboard is not loaded yet, loading from start")
            return await self.get_leaderboard(length=length)

        api_client = _APIClient()
        leaderboards = await api_client.get(
            _TMIO.build([_TMIO.TABS.LEADERBOARD, _TMIO.TABS.MAP, self.uid])
            + f"?offset={self._offset}&length={length}"
        )
        await api_client.close()

        with suppress(KeyError, TypeError):
            raise TMIOException(leaderboards["error"])
        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            _log.debug(f"Caching leaderboard {self.uid}:{self.offset}:{self.length}")
            cache_client.set(
                f"leaderboard:{self.uid}:{self.offset}:{self.length}",
                json.dumps(leaderboards),
            )

        self._offset += length
        self._lb_loaded = True

        lbs = []
        for lb in leaderboards["tops"]:
            lbs.append(Leaderboard._from_dict(lb))

        return lbs
