import json
import logging
from contextlib import suppress
from datetime import datetime
from typing import Dict, List

import redis
from typing_extensions import Self

from trackmania.api import _APIClient

from .api import _APIClient
from .config import Client
from .constants import _TMX
from .errors import InvalidTMXCode

_log = logging.getLogger(__name__)

__all__ = (
    "TMXMapTimes",
    "GbxFileMetadata",
    "TMXTags",
    "ReplayWRData",
    "TMXMetadata",
    "TMXMap",
)


async def _get_map(tmx_id: int) -> Dict:
    _log.info(f"Getting map data for tmx id {tmx_id}")

    cache_client = Client._get_cache_client()
    with suppress(ConnectionError, redis.exceptions.ConnectionError):
        if cache_client.exists(f"tmxmap:{tmx_id}"):
            _log.debug(f"Found map data for tmx id {tmx_id} in cache")
            return json.loads(cache_client.get(f"tmxmap:{tmx_id}").decode("utf-8"))

    api_client = _APIClient()
    map_data = await api_client.get(
        _TMX.build([_TMX.TABS.MAPS, _TMX.TABS.GET_MAP_INFO, _TMX.TABS.ID, tmx_id])
    )
    await api_client.close()

    if not isinstance(map_data, dict):
        raise InvalidTMXCode("Invalid TMX code")
    with suppress(ConnectionError, redis.exceptions.ConnectionError):
        _log.debug(f"Caching map data for tmx id {tmx_id}")
        cache_client.set(f"tmxmap:{tmx_id}", json.dumps(map_data))

    return map_data


class TMXMapTimes:
    """
    .. versionadded :: 0.3.3

    Represents when the map was uploaded and/or updated on the `trackmania.exchange` website

    Parameters
    ----------
    uploaded : :class:`datetime`
        When the map was uploaded to TMX
    updated : :class:`datetime`
        When the map was last updated on TMX
    """

    def __init__(self, uploaded: datetime, updated: datetime):
        self.uploaded = uploaded
        self.updated = updated

    @classmethod
    def _from_dict(cls: Self, raw: Dict) -> Self:
        _log.debug("Creating a TMXMapTimes from given dictionary")

        uploaded_raw, updated_raw = raw.get("UploadedAt"), raw.get("UpdatedAt")

        # 2022-03-15T18:18:50.007 to datetime
        uploaded = datetime.strptime(uploaded_raw, "%Y-%m-%dT%H:%M:%S.%f")
        updated = datetime.strptime(updated_raw, "%Y-%m-%dT%H:%M:%S.%f")

        return cls(uploaded, updated)


class GbxFileMetadata:
    """
    .. versionadded :: 0.3.3

    Represents data stored in the map's GBX file metadata

    Parameters
    ----------
    gbx_map_name : str
        Unaltered map name
    author_login : str
        Unaltered author name
    map_type : str
        Nadeo map type embedded.
    title_pack : str
        Titlepack of map
    track_uid : str
        Unaltered map signature `uid`
    mood : str
        Mood of the map (daytime and map base)
    display_cost : int
        in game metric for map weight
    mod_name : str | None
        Name of texture mod, if included
    light_map : int
        Light map version
    exe_version : str
        Game application version
    exe_build : :class:`datetime`
        Build date of game version
    author_time : int
        Map author time in ms
    environment_name : str
        Name of the game environment
    vehicle_name : str
        Name of the game vehicle
    """

    def __init__(
        self,
        gbx_map_name: str,
        author_login: str,
        map_type: str,
        title_pack: str,
        track_uid: str,
        mood: str,
        display_cost: int,
        mod_name: str,
        light_map: int,
        exe_version: str,
        exe_build: datetime,
        author_time: int,
        environment_name: str,
        vehicle_name: str,
    ):
        self.gbx_map_name = gbx_map_name
        self.author_login = author_login
        self.map_type = map_type
        self.title_pack = title_pack
        self.track_uid = track_uid
        self.mood = mood
        self.display_cost = display_cost
        self.mod_name = mod_name
        self.light_map = light_map
        self.exe_version = exe_version
        self.exe_build = exe_build
        self.author_time = author_time
        self.environment_name = environment_name
        self.vehicle_name = vehicle_name

    @classmethod
    def _from_dict(cls: Self, raw: Dict) -> Self:
        _log.debug("Creating a GbxFileMetadata from given dictionary")

        args = [
            raw.get("GbxMapName"),
            raw.get("AuthorLogin"),
            raw.get("MapType"),
            raw.get("TitlePack"),
            raw.get("TrackUID"),
            raw.get("Mood"),
            raw.get("DisplayCost"),
            raw.get("ModName"),
            raw.get("Lightmap"),
            raw.get("ExeVersion"),
            datetime.strptime(raw.get("ExeBuild"), "%Y-%m-%d_%H_%M"),
            raw.get("AuthorTime"),
            raw.get("EnvironmentName"),
            raw.get("VehicleName"),
        ]

        return cls(*args)


class TMXTags:
    """
    .. versionadded :: 0.3.3

    Represents TMX Map Tags

    Parameters
    ----------
    map_tags : :class:`List[int]`
        The map tags as a list of integers
    """

    def __init__(self, map_tags: List[int]):
        self.map_tags = map_tags

    @classmethod
    def _from_dict(cls: Self, raw: Dict) -> Self:
        _log.debug("Creating a TMXTags from given dictionary")

        map_tags_ss = raw.get("Tags", None).split(",")
        map_tags = []

        for tag in map_tags_ss:
            map_tags.append(int(tag))

        return cls(map_tags)

    def __str__(self) -> str:
        return ", ".join([_TMX.MAP_TYPE_ENUMS.get(tag) for tag in self.map_tags])


class ReplayWRData:
    """
    .. versionadded :: 0.3.3

    Represents data relating to the wr replay

    Parameters
    ---------
    wr_id : int | None
        replay id of mx world record
    wr_time: int | None
        Time of the mx world record
    wr_user_id: int | None
        userid of the mx world record holder
    wr_username: str
        mx username of max world record holder
    """

    def __init__(
        self,
        wr_id: int | None,
        wr_time: int | None,
        wr_user_id: int | None,
        wr_username: str,
    ):
        self.wr_id = wr_id
        self.wr_time = wr_time
        self.wr_user_id = wr_user_id
        self.wr_username = wr_username

    @classmethod
    def _from_dict(cls: Self, raw: Dict) -> Self:
        _log.debug("Creating a ReplayWRData from given dictionary")

        args = [
            raw.get("ReplayWRId"),
            raw.get("ReplayWRTime"),
            raw.get("ReplayWRUserID"),
            raw.get("ReplayWRUsername"),
        ]

        return cls(*args)


class TMXMetadata:
    """
    .. versionadded :: 0.3.3

    Represents a map's metadata on TMX

    Parameters
    ----------
    unlisted : bool
        Whether the map is unlisted on TMX
    unreleased : bool
        Whether the map is unreleased on TMX
    downloadeable : bool
        Whether the map is downloadeable on TMX
    rating_vote_count : int
        The number of votes for the map
    rating_vote_average : float
        The average rating of the map
    has_screenshot : bool
        Whether the map has a screenshot
    has_thumbnail : bool
        Whether the map has a thumbnail
    has_ghost_blocks : bool
        Whether the map has ghost blocks
    embedded_objects_count : int
        The number of embedded objects on the map
    embedded_objects_size : int
        The size of the embedded objects on the map
    size_warning : bool
        Map exceeds the size limit for online servers (TM: 6MB)
    replay_count : int
        The number of replays on the map
    award_count : int
        The number of awards on the map
    comments_count : int
        The number of comments on the map
    image_count : int
        The number of custom images on the map
    video_count : int
        The number of videos on the map
    """

    def __init__(
        self,
        unlisted: bool,
        unreleased: bool,
        downloadable: bool,
        rating_vote_count: int,
        rating_vote_average: float,
        has_screenshot: bool,
        has_thumbnail: bool,
        has_ghost_blocks: bool,
        embedded_objects_count: int,
        embedded_objects_size: int,
        size_warning: bool,
        replay_count: int,
        award_count: int,
        comment_count: int,
        image_count: int,
        video_count: int,
    ):
        self.unlisted = unlisted
        self.unreleased = unreleased
        self.downloadable = downloadable
        self.rating_vote_count = rating_vote_count
        self.rating_vote_average = rating_vote_average
        self.has_screenshot = has_screenshot
        self.has_thumbnail = has_thumbnail
        self.has_ghost_blocks = has_ghost_blocks
        self.embedded_objects_count = embedded_objects_count
        self.embedded_objects_size = embedded_objects_size
        self.size_warning = size_warning
        self.replay_count = replay_count
        self.award_count = award_count
        self.comment_count = comment_count
        self.image_count = image_count
        self.video_count = video_count

    @classmethod
    def _from_dict(cls: Self, raw: Dict) -> Self:
        _log.debug("Creating a TMXMetaData from given dictionary")

        args = [
            raw.get("Unlisted"),
            raw.get("Unreleased"),
            raw.get("Downloadable"),
            raw.get("RatingVoteCount"),
            raw.get("RatingVoteAverage"),
            raw.get("HasScreenshot"),
            raw.get("HasThumbnail"),
            raw.get("HasGhostBlocks"),
            raw.get("EmbeddedObjectsCount"),
            raw.get("EmbeddedItemsSize"),
            raw.get("SizeWarning"),
            raw.get("ReplayCount"),
            raw.get("AwardCount"),
            raw.get("CommentCount"),
            raw.get("ImageCount"),
            raw.get("VideoCount"),
        ]

        return cls(*args)


class TMXMap:
    """
    .. versionadded :: 0.3.3

    Represents a Map from TMX

    Parameters
    ----------
    username : str
        The username of the map's creator
    track_id : int | None
        The track id of the map
    map_id : int | None
        The map id of the map
    comments : str
        Map author's comments
    map_pack_id : str
        The map pack id of the map
    user_id : int
        The user id of the map's creator
    route_name : str
        The route name of the map
    length_name : str
        The length name of the map
    difficulty_name : str
        The difficulty name of the map
    laps : int
        The number of laps of the map
    times: :class:`TMXMapTimes`
        The uploaded and updated at times of the map.
    gbx_data : :class:`GbxFileMetadata`
        The gbx file metadata of the map
    tags : :class:`TMXTags`
        The tags of the map
    replay_wr_data : :class:`ReplayWRData`
        The replay wr data of the map
    metadata : :class:`TMXMetadata`
        The metadata of the map
    """

    def __init__(
        self,
        username: str,
        track_id: int | None,
        map_id: int | None,
        comments: str,
        map_pack_id: str,
        user_id: int,
        route_name: str,
        length_name: str,
        difficulty_name: str,
        laps: int,
        times: TMXMapTimes,
        gbx_data: GbxFileMetadata,
        tags: TMXTags,
        replay_wr_data: ReplayWRData,
        metadata: TMXMetadata,
    ):
        self.username = username
        self.track_id = track_id
        self.map_id = map_id
        self.comments = comments
        self.map_pack_id = map_pack_id
        self.user_id = user_id
        self.route_name = route_name
        self.length_name = length_name
        self.difficulty_name = difficulty_name
        self.laps = laps
        self.times = times
        self.gbx_data = gbx_data
        self.tags = tags
        self.replay_wr_data = replay_wr_data
        self.metadata = metadata

    @classmethod
    def _from_dict(cls: Self, raw: Dict) -> Self:
        _log.debug("Creating a TMXMap from given dictionary")

        username = raw.get("Username")
        track_id = raw.get("TrackID")
        map_id = raw.get("MapID")
        comments = raw.get("Comments")
        map_pack_id = raw.get("MappackID")
        user_id = raw.get("UserID")
        route_name = raw.get("RouteName")
        length_name = raw.get("LengthName")
        difficulty_name = raw.get("DifficultyName")
        laps = raw.get("Laps")
        times = TMXMapTimes._from_dict(raw)
        gbx_data = GbxFileMetadata._from_dict(raw)
        tags = TMXTags._from_dict(raw)
        replay_wr_data = ReplayWRData._from_dict(raw)
        metadata = TMXMetadata._from_dict(raw)

        args = [
            username,
            track_id,
            map_id,
            comments,
            map_pack_id,
            user_id,
            route_name,
            length_name,
            difficulty_name,
            laps,
            times,
            gbx_data,
            tags,
            replay_wr_data,
            metadata,
        ]

        return cls(*args)

    @classmethod
    async def get_map(cls: Self, tmx_id: int) -> Self:
        """
        .. versionadded :: 0.3.3

        Gets a map's data using it's tmx id

        Parameters
        ----------
        tmx_id : int
            The tmx id
        """
        tmx_map_data = await _get_map(tmx_id)
        return cls._from_dict(tmx_map_data)
