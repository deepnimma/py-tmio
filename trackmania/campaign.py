import logging
from contextlib import suppress
from datetime import datetime

import redis
from typing_extensions import Self

from trackmania.errors import TMIOException

from .api import _APIClient
from .config import Client, get_from_cache, set_in_cache
from .constants import _TMIO
from .player import Player
from .tmmap import TMMap

_log = logging.getLogger(__name__)


class OfficialCampaignMedia:
    """
    .. versionadded :: 0.5

    Media images of official campaigns

    Parameters
    ----------
    button_background : str
        The button background image URL of the campaign.
    button_foreground : str
        The button foreground image URL of the campaign.
    decal : str
        The decal image URL of the campaign
    live_button_background : str
        The live button background image URL of the campaign.
    live_button_foreground : str
        The live button foreground image URL of the campaign.
    popup : str
        The popup image URL of the campaign.
    popup_background : str
        The popup background image URL of the campaign.
    """

    def __init__(
        self,
        button_background: str,
        button_foreground: str,
        decal: str,
        live_button_background: str,
        live_button_foreground: str,
        popup: str,
        popup_background: str,
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

        return cls(*args)


class CampaignLeaderboard:
    def __init__(
        self,
        player_name: str,
        player_id: str,
        points: int,
        position: int,
    ):
        self.player_name = player_name
        self.player_id = player_id
        self.points = points
        self.position = position

    async def player(self) -> Player:
        """
        Returns the player object of this campaign leaderboard position

        Returns
        -------
        :class:`Player`
            The player who achieved this position on the leaderboard.
        """
        return await Player.get_player(self.player_id)


class CampaignSearchResult:
    """
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
        club_id = raw_data.get("clubid", 0)
        date = datetime.utcfromtimestamp(raw_data.get("timestamp", 0))
        campaign_id = raw_data.get("id", 0)
        map_count = raw_data.get("mapcount", 1)
        name = raw_data.get("name")

        args = [
            club_id,
            date,
            campaign_id,
            map_count,
            name,
        ]

        return cls(*args)

    def get_campaign(self):
        return Campaign.get_campaign(self.campaign_id, self.club_id)


class Campaign:
    """
    .. versionadded :: 0.5

    Represents a Campaign in Trackmania 2020.

    Parameters
    ----------
    created_at : datetime
        The date the campaign was created
    campaign_id : int
        The campaign's ID
    image : str
        The image URL of the campaign.
        Returns the decal image if this is an official campaign
    is_official : bool
        Whether the camapaign is official (made by Nadeo).
    leaderboard_id : str
        The campaign's leaderboard id.
    map_count : int
        The number of maps in the campaign.
    media : :class:`OfficialCampaignMedia` | None
        The media of the campaign only if it is on official campaign.
    name : str
        The name of the campaign
    updated_at : datetime
        The date the campaign was last updated
    """

    def __init__(
        self,
        campaign_id: int,
        image: str,
        is_official: bool,
        leaderboard_uid: str,
        maps: list[TMMap],
        map_count: int,
        media: OfficialCampaignMedia | None,
        name: str,
    ):
        self.campaign_id = campaign_id
        self.image = image
        self.is_official = is_official
        self.leaderboard_uid = leaderboard_uid
        self.maps = maps
        self.map_count = map_count
        self.media = media
        self.name = name

    @classmethod
    def _from_dict(cls: Self, raw_data: dict, official: bool = False) -> Self:
        campaign_id = raw_data.get("id")
        image = raw_data.get("media")
        is_official = official
        leaderboard_uid = raw_data.get("leaderboarduid")
        maps = [TMMap._from_dict(map_data) for map_data in raw_data.get("playlist", [])]
        map_count = len(raw_data.get("playlist", []))
        if raw_data.get("mediae") is not None:
            media = OfficialCampaignMedia._from_dict(raw_data.get("mediae"))
        else:
            media = None
        name = raw_data.get("name")

        args = [
            campaign_id,
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
        Gets a campaign with the given campaign and club ids.

        Parameters
        ----------
        campaign_id : int
            The campaign's id.
        club_id : int
            The club the campaign belongs to.

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
        Gets all official nadeo campaigns.

        Returns
        -------
        :class:`list[CampaignSearchResult]`
            The list of campaigns.
        """
        official_campaigns = []
        all_campaigns = get_from_cache("campaigns:all:0")

        if all_campaigns is not None:
            for campaign in all_campaigns:
                if campaign.get("id", -1) == 0:
                    official_campaigns.append(CampaignSearchResult._from_dict(campaign))
            return official_campaigns

        api_client = _APIClient()
        all_campaigns = await api_client.get(_TMIO.build([_TMIO.TABS.CAMPAIGNS, 0]))
        await api_client.close()

        with suppress(KeyError, TypeError):
            raise TMIOException(all_campaigns["error"])

        set_in_cache("campaigns:all:0", all_campaigns, ex=432000)

        for campaign in all_campaigns:
            if campaign.get("id", -1) == 0:
                official_campaigns.append(CampaignSearchResult._from_dict(campaign))

        return official_campaigns

    @staticmethod
    async def popular_campaigns(page: int = 0) -> list[CampaignSearchResult]:
        """
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
            for campaign in all_campaigns:
                if campaign.get("clubid", -1) != 0:
                    campaigns_list.append(CampaignSearchResult._from_dict(campaign))

        api_client = _APIClient()
        all_campaigns = await api_client.get(_TMIO.build([_TMIO.TABS.CAMPAIGNS, page]))
        await api_client.close()

        with suppress(KeyError, TypeError):
            raise TMIOException(all_campaigns["error"])

        for campaign in all_campaigns:
            if campaign.get("clubid", -1) != 0:
                campaigns_list.append(CampaignSearchResult._from_dict(campaign))

        return campaigns_list
