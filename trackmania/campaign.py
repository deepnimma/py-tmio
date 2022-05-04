import logging
from contextlib import suppress
from datetime import datetime

from typing_extensions import Self

from ._util import _regex_it
from .api import _APIClient
from .club import Club
from .config import get_from_cache, set_in_cache
from .constants import _TMIO
from .errors import TMIOException
from .player import Player
from .tmmap import TMMap

_log = logging.getLogger(__name__)

__all__ = (
    "OfficialCampaignMedia",
    "CampaignSearchResult",
    "CampaignLeaderboard",
    "Campaign",
)


class OfficialCampaignMedia:
    """
    .. versionadded :: 0.5

    Media images of official campaigns

    Parameters
    ----------
    button_background : str | None
        The button background image URL of the campaign.
    button_foreground : str | None
        The button foreground image URL of the campaign.
    decal : str | None
        The decal image URL of the campaign
    live_button_background : str | None
        The live button background image URL of the campaign.
    live_button_foreground : str | None
        The live button foreground image URL of the campaign.
    popup : str | None
        The popup image URL of the campaign.
    popup_background : str | None
        The popup background image URL of the campaign.
    """

    def __init__(
        self,
        button_background: str | None = None,
        button_foreground: str | None = None,
        decal: str | None = None,
        live_button_background: str | None = None,
        live_button_foreground: str | None = None,
        popup: str | None = None,
        popup_background: str | None = None,
    ):
        self.button_background = button_background
        self.button_foreground = button_foreground
        self.decal = decal
        self.live_button_background = live_button_background
        self.live_button_foreground = live_button_foreground
        self.popup = popup
        self.popup_background = popup_background

    @classmethod
    def _from_dict(cls: Self, raw_data: dict) -> Self:
        _log.debug("Creating an OfficialCampaignsMedia class from given dictionary")
        button_background = raw_data.get("buttonbackground")
        button_foreground = raw_data.get("buttonforeground")
        decal = raw_data.get("decal")
        live_button_background = raw_data.get("livebuttonbackground")
        live_button_foreground = raw_data.get("livebuttonforeground")
        popup = raw_data.get("popup")
        popup_background = raw_data.get("popup_background")

        args = [
            button_background,
            button_foreground,
            decal,
            live_button_background,
            live_button_foreground,
            popup,
            popup_background,
        ]

        for i, argument in enumerate(args):
            if str(argument) == "":
                args[i] = None

        return cls(*args)


class CampaignSearchResult:
    """
    .. versionadded :: 0.5

    Represents a CampaignSearchResult.

    Parameters
    ----------
    club_id : int
        The ID of the club that created the campaign.
    date : datetime
        The date the campaign was created.
    campaign_id : int
        The ID of the campaign.
    map_count : int
        The number of maps in the campaign.
    name : str
        The name of the campaign.
    """

    def __init__(
        self,
        club_id: int,
        date: datetime,
        campaign_id: int,
        map_count: int,
        name: int,
    ):
        self.club_id = club_id
        self.date = date
        self.campaign_id = campaign_id
        self.map_count = map_count
        self.name = name

    @classmethod
    def _from_dict(cls: Self, raw_data: dict) -> Self:
        _log.debug("Creating a CampaignSearchResult class from given dictionary")
        club_id = raw_data.get("clubid", 0)
        date = datetime.utcfromtimestamp(raw_data.get("timestamp", 0))
        campaign_id = raw_data.get("id", 0)
        map_count = raw_data.get("mapcount", 1)
        name = _regex_it(raw_data.get("name"))

        args = [
            club_id,
            date,
            campaign_id,
            map_count,
            name,
        ]

        return cls(*args)

    def get_campaign(self):
        """
        .. versionadded :: 0.5

        Gets the campaign object.

        Returns
        -------
        :class:`Campaign`
            The campaign object.
        """
        return Campaign.get_campaign(self.campaign_id, self.club_id)


class CampaignLeaderboard:
    """
    .. versionadded :: 0.5

    Represents a player on the Campaign's point leaderboards

    Parameters
    ----------
    player_name : str
        The name of the player who got the position.
    player_id : str
        The ID of the player who got the position.
    player_tag : str | None
        The tag of the player who got the position.
    position : int
        The position the player achieved.
    points : int
        The points the player has
    """

    def __init__(
        self,
        player_name: str,
        player_id: str,
        player_tag: str | None,
        position: int,
        points: int,
    ):
        self.player_name = player_name
        self.player_id = player_id
        self.player_tag = player_tag
        self.position = position
        self.points = points

    @classmethod
    def _from_dict(cls: Self, raw_data: dict) -> Self:
        player_name = raw_data["player"]["name"]
        player_id = raw_data["player"]["id"]
        player_tag = _regex_it(raw_data["player"].get("tag", None))
        position = raw_data["position"]
        points = raw_data["points"]

        args = [
            player_name,
            player_id,
            player_tag,
            position,
            points,
        ]

        return cls(*args)

    async def player(self) -> Player:
        """
        .. versionadded :: 0.5

        Gets the player this position belongs to.

        Returns
        -------
        :class:`Player`
            The player that holds this position.
        """
        return await Player.get_player(self.player_id)


class Campaign:
    """
    .. versionadded :: 0.5

    Represents a Campaign in Trackmania 2020.

    Parameters
    ----------
    campaign_id : int
        The campaign's ID
    club_id : int
        The club's id.
    image : str | None
        The image URL of the campaign.
        Returns the decal image if this is an official campaign.
        NoneType if there is no decal image.
    is_official : bool
        Whether the camapaign is official (made by Nadeo).
    leaderboard_uid : str
        The campaign's leaderboard id.
    maps : :class:`list[TMMap]`
        The maps in the campaign.
    map_count : int
        The number of maps in the campaign.
    media : :class:`OfficialCampaignMedia` | None
        The media of the campaign only if it is on official campaign.
    name : str
        The name of the campaign
    """

    def __init__(
        self,
        campaign_id: int,
        club_id: int,
        image: str,
        is_official: bool,
        leaderboard_uid: str,
        maps: list[TMMap],
        map_count: int,
        media: OfficialCampaignMedia | None,
        name: str,
    ):
        self.campaign_id = campaign_id
        self.club_id = club_id
        self.image = image
        self.is_official = is_official
        self.leaderboard_uid = leaderboard_uid
        self.maps = maps
        self.map_count = map_count
        self.media = media
        self.name = name

    @classmethod
    def _from_dict(cls: Self, raw_data: dict, official: bool = False) -> Self:
        _log.debug("Creating a Campaign class from given dictionary")
        campaign_id = raw_data.get("id")
        club_id = raw_data.get("clubid", 0)
        image = raw_data.get("media") if raw_data.get("media") != "" else None
        is_official = official
        leaderboard_uid = raw_data.get("leaderboarduid")
        maps = [TMMap._from_dict(map_data) for map_data in raw_data.get("playlist", [])]
        map_count = len(raw_data.get("playlist", []))
        if raw_data.get("mediae") is not None:
            media = OfficialCampaignMedia._from_dict(raw_data.get("mediae"))
        else:
            media = None
        name = _regex_it(raw_data.get("name"))

        args = [
            campaign_id,
            club_id,
            image,
            is_official,
            leaderboard_uid,
            maps,
            map_count,
            media,
            name,
        ]

        return cls(*args)

    @classmethod
    async def get_campaign(cls: Self, campaign_id: int, club_id: int) -> Self | None:
        """
        .. versionadded :: 0.5

        Gets a campaign with the given campaign and club ids.
        If it's an official campaign, the `club_id` should be = 0


        Parameters
        ----------
        campaign_id : int
            The campaign's id.
        club_id : int
            The club the campaign belongs to.
            = 0 if the campaign is an official nadeo campaign.

        Returns
        -------
        :class:`Campaign` | None
            The campaign object, None if it does not exist
        """
        official = True if club_id == 0 else False
        campaign_data = get_from_cache(f"campaign:{campaign_id}:{club_id}")
        if campaign_data is not None:
            return cls._from_dict(campaign_data, official=official)

        api_client = _APIClient()
        if club_id != 0:
            campaign_data = await api_client.get(
                _TMIO.build([_TMIO.TABS.CAMPAIGN, club_id, campaign_id])
            )
        else:
            campaign_data = await api_client.get(
                _TMIO.build([_TMIO.TABS.OFFICIAL_CAMPAIGN, campaign_id])
            )
        await api_client.close()

        set_in_cache(f"campaign:{campaign_id}:{club_id}", campaign_data, ex=432000)

        return cls._from_dict(campaign_data, official=official)

    @classmethod
    async def current_season(cls: Self) -> Self:
        """
        .. versionadded :: 0.5

        Gets the current seasonal campaign.

        Returns
        -------
        :class:`Campaign`
            The campaign.
        """
        api_client = _APIClient()
        campaign_data = await api_client.get(_TMIO.build([_TMIO.TABS.CAMPAIGNS, 0]))
        await api_client.close()

        with suppress(KeyError, TypeError):
            raise TMIOException(campaign_data["error"])

        campaign_id = campaign_data.get("campaigns", [])[0].get("id")

        return await cls.get_campaign(campaign_id, 0)

    @staticmethod
    async def official_campaigns() -> list[CampaignSearchResult]:
        """
        .. versionadded :: 0.5

        Gets all official nadeo campaigns.

        Returns
        -------
        :class:`list[CampaignSearchResult]`
            The list of campaigns.
        """
        official_campaigns = []
        all_campaigns = get_from_cache("campaigns:all:0")

        if all_campaigns is not None:
            for campaign in all_campaigns.get("campaigns", []):
                if campaign.get("clubid", -1) == 0:
                    official_campaigns.append(CampaignSearchResult._from_dict(campaign))
            return official_campaigns

        api_client = _APIClient()
        all_campaigns = await api_client.get(_TMIO.build([_TMIO.TABS.CAMPAIGNS, 0]))
        await api_client.close()

        with suppress(KeyError, TypeError):
            raise TMIOException(all_campaigns["error"])

        set_in_cache("campaigns:all:0", all_campaigns, ex=432000)

        for campaign in all_campaigns.get("campaigns", []):
            if campaign.get("id", -1) == 0:
                official_campaigns.append(CampaignSearchResult._from_dict(campaign))

        return official_campaigns

    @staticmethod
    async def popular_campaigns(page: int = 0) -> list[CampaignSearchResult]:
        """
        .. versionadded :: 0.5

        Gets all popular campaigns, official campaigns excluded.
        50 Results / Page (except Page 1 because of the official campaigns)

        Parameters
        ----------
        page : int, optional
            The page number, by default 0

        Returns
        -------
        :class:`list[CampaignSearchResult]`
            The list of campaigns.
        """
        campaigns_list = []
        all_campaigns = get_from_cache(f"campaigns:all:{page}")

        if all_campaigns is not None:
            for campaign in all_campaigns.get("campaigns", []):
                if campaign.get("clubid", -1) != 0:
                    campaigns_list.append(CampaignSearchResult._from_dict(campaign))

        api_client = _APIClient()
        all_campaigns = await api_client.get(_TMIO.build([_TMIO.TABS.CAMPAIGNS, page]))
        await api_client.close()

        with suppress(KeyError, TypeError):
            raise TMIOException(all_campaigns["error"])

        for campaign in all_campaigns.get("campaigns", []):
            if campaign.get("clubid", -1) != 0:
                campaigns_list.append(CampaignSearchResult._from_dict(campaign))

        return campaigns_list

    async def club(self) -> Club:
        """
        .. versionadded :: 0.5

        The club the Campaign belongs to.

        Returns
        -------
        :class:`Club` | None
            The Club the campaign belongs to. If it does not belong to a campaign returns None.
        """
        if self.club_id == 0:
            return None
        else:
            return await Club.get_club(self.club_id)

    async def leaderboards(
        self, offset: int = 0, length: int = 100
    ) -> list[CampaignLeaderboard]:
        """
        .. versionadded :: 0.5

        Gets the points leaderboards for the campaign.

        Parameters
        ----------
        offset : int, optional
            The leaderboard offset to start at, by default 0
        length : int, optional
            The length of the leaderboard to get. Can only be between 0 and 100, by default 100

        Returns
        -------
        :class:`list[CampaignLeaderboard]`
            The leaderboard of the campaign based on points.
        """
        leaderboards = []
        leaderboard_data = get_from_cache(
            f"campaign:{self.campaign_id}:{offset}:{length}"
        )

        if leaderboard_data is not None:
            for lb_place in leaderboard_data.get("tops", []):
                leaderboards.append(CampaignLeaderboard._from_dict(lb_place))

            return leaderboards

        api_client = _APIClient()
        leaderboard_data = await api_client.get(
            _TMIO.build([_TMIO.TABS.LEADERBOARD, self.leaderboard_uid])
            + f"?offset={offset}&length={length}"
        )
        await api_client.close()

        with suppress(KeyError, TypeError):
            raise TMIOException(leaderboard_data["error"])

        set_in_cache(
            f"campaign:{self.campaign_id}:{offset}:{length}",
            leaderboard_data,
            ex=432000,
        )

        for lb_place in leaderboard_data.get("tops", []):
            leaderboards.append(CampaignLeaderboard._from_dict(lb_place))

        return leaderboards

    def get_map(self: Self, index: int = 0) -> TMMap:
        """
        .. versionadded :: 0.5

        Gets a map at a specific index.

        Parameters
        ----------
        index : int, optional
            The index of the map requested, by default 0

        Returns
        -------
        :class:`TMMap`
            The map at the index.
        """
        return self.maps[index]
