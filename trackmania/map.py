import json
import logging
from contextlib import suppress
from datetime import datetime
from typing import Dict, List

import redis

from trackmania.api import APIClient

from .api import APIClient
from .config import Client
from .constants import TMIO
from .errors import TMIOException
from .player import Player

_log = logging.getLogger(__name__)

__all__ = (
    "MedalTimes",
    "Leaderboard",
    "Map",
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
        sec, ms = divmod(time, 1000)
        min, sec = divmod(time, 60)

        return f"{min:02d}:{sec:02d}.{ms:03d}"


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
    position : int
        The position of the player in the leaderboard
    time : int
        The time of the player in the leaderboard
    player : :class:`Player` | :class:`Dict` | :class:`NoneType`, optional
        The player object of the player
    """

    def __init__(
        self,
        timestamp: datetime,
        ghost: str,
        player_club_tag: str | None,
        player_name: str | None,
        position: int,
        time: int,
        player: Player | Dict | None = None,
    ):
        self.timestamp = timestamp
        self.ghost = ghost
        self.player_club_tag = player_club_tag
        self.player_name = player_name
        self.position = position
        self.time = time

        if isinstance(player, dict):
            self._player = Player._from_dict(player)
        else:
            self._player = player

    @classmethod
    def _from_dict(cls, raw: Dict):
        player = Player._from_dict(raw["player"]) if "player" in raw else None
        player_name = raw["player"]["name"] if "player" in raw else None
        player_club_tag = (
            raw["player"]["tag"] if "player" in raw and "tag" in raw["player"] else None
        )
        position = raw["position"]
        time = raw["time"]
        ghost = raw["url"]
        timestamp = datetime.strptime(raw["timestamp"], "%Y-%m-%dT%H:%M:%S+00:00")

        return cls(
            timestamp=timestamp,
            ghost=ghost,
            player_club_tag=player_club_tag,
            player_name=player_name,
            position=position,
            time=time,
            player=player,
        )

    @property
    def player(self) -> Player:
        return self._player


class Map:
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
    def _from_dict(cls, raw: Dict):
        author_id = raw["author"]
        author_name = raw["authorplayer"]["name"]
        environment = raw["collectionName"]
        exchange_id = raw["exchangeid"] if "exchangeid" in raw else None
        file_name = raw["filename"]
        map_id = raw["mapId"]
        leaderboard = None
        medal_time = MedalTimes(
            raw["bronzeScore"], raw["silverScore"], raw["goldScore"], raw["authorScore"]
        )
        name = raw["name"]
        submitter_id = raw["submitter"]
        submitter_name = raw["submitterplayer"]["name"]
        thumbnail = raw["thumbnailUrl"]
        uid = raw["mapUid"]
        uploaded = datetime.strptime(raw["timestamp"], "%Y-%m-%dT%H:%M:%S+00:00")
        url = raw["fileUrl"]

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

    @staticmethod
    async def get(map_uid: str):
        """
        .. versionadded :: 0.3.0

        Gets the TM Map from the Map's UID

        Parameters
        ----------
        map_uid : str
            The map's UID
        """
        cache_client = redis.Redis(
            host=Client.REDIS_HOST,
            port=Client.REDIS_PORT,
            db=Client.REDIS_DB,
            password=Client.REDIS_PASSWORD,
        )

        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            if cache_client.exists(f"map:{map_uid}"):
                _log.debug(f"Map {map_uid} found in cache")
                return Map._from_dict(json.loads(cache_client.get(f"map:{map_uid}")))

        api_client = APIClient()
        map_data = await api_client.get(TMIO.build([TMIO.TABS.MAP, map_uid]))
        await api_client.close()

        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            _log.debug(f"Caching map {map_uid}")
            cache_client.set(f"map:{map_uid}", json.dumps(map_data))

        return Map._from_dict(map_data)

    async def author(self) -> Player:
        """
        .. versionadded :: 0.3.0

        Returns the author as a player.

        Returns
        -------
        :class:`Player`
            The author as a :class:`Player` object
        """
        return await Player.get(self.author_id)

    async def submitter(self) -> Player:
        """
        .. versionadded :: 0.3.0

        Returns the submitter as a player.

        Returns
        -------
        :class:`Player`
            The submitter as a :class:`Player` object
        """
        return await Player.get(self.submitter_id)

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
        elif length > 100:
            length = 100

        cache_client = redis.Redis(
            host=Client.REDIS_HOST,
            port=Client.REDIS_PORT,
            db=Client.REDIS_DB,
            password=Client.REDIS_PASSWORD,
        )

        self._offset = offset
        self.length = length

        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            if cache_client.exists(
                f"leaderboard:{self.map_id}:{self.offset}:{self.length}"
            ):
                _log.debug(
                    f"Leaderboard {self.map_id}:{self.offset}:{self.length} found in cache"
                )
                leaderboards = list()
                for lb in json.loads(
                    cache_client.get(
                        f"leaderboard:{self.map_id}:{self.offset}:{self.length}"
                    ).decode("utf-8")
                )["tops"]:
                    leaderboards.append(Leaderboard._from_dict(lb))

                return leaderboards

        api_client = APIClient()
        lb_data = await api_client.get(
            TMIO.build([TMIO.TABS.LEADERBOARD, TMIO.TABS.MAP, self.map_id])
            + f"offset={self.offset}&length={self.length}"
        )
        await api_client.close()

        with suppress(KeyError, TypeError):
            _log.error("This is a trackmania.io error")
            raise TMIOException(lb_data["error"])
        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            _log.debug(f"Caching leaderboard {self.map_id}:{self.offset}:{self.length}")
            cache_client.set(
                f"leaderboard:{self.map_id}:{self.offset}:{self.length}",
                json.dumps(lb_data),
            )

        self._offset += self.length
        self._lb_loaded = True

        leaderboards = list()
        for lb in lb_data["tops"]:
            leaderboards.append(Leaderboard._from_dict(lb))

        return leaderboards
