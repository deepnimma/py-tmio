# pylint: disable=too-many-instance-attributes
from typing import List

__all__ = ("TMIO", "TMX")

# pylint: disable=too-few-public-methods
class TMIOTabs:
    """TMIO Endpoints"""

    def __init__(self):
        self.player: str = "player"
        self.players: str = "players"
        self.trophies: str = "trophies"
        self.map: str = "map"
        self.leaderboard: str = "leaderboard"

        self.top_matchmaking: str = "top/matchmaking"
        self.top_trophies: str = "top/trophies"

        self.matchmaking_id: int = 2
        self.royal_id: int = 3

        self.totd: str = "totd"
        self.ads: str = "ads"


# pylint: disable=too-few-public-methods
class TMIO:
    """Basic TMIO Api Details

    :param protocol: The protocol to use for the api. Equal to
            "https"
    :type protocol: str
    :param base: The base url for the api. Equal to "trackmania.io"
    :type base: str
    :param api: The api endpoint for `trackmania.io`. Equal to "api".
    :type api: str
    :param tabs (: class:`TMIOTabs`): The tabs for the api.

    """

    protocol: str = "https"
    base: str = "trackmania.io"
    api: str = "api"

    tabs: TMIOTabs = TMIOTabs()

    @staticmethod
    def build(endpoints: List[str]) -> str:
        """Builds a TMIO endpoint url.

        :param endpoints: The endpoints to build the url with.
        :type endpoints: List[str]
        :param endpoints: List[str]:
        :returns: The built endpoint url.
        :rtype: str

        """
        url = f"{TMIO.protocol}://{TMIO.base}/{TMIO.api}/"

        if len(endpoints) == 0:
            return url
        if len(endpoints) > 1:
            for item in endpoints:
                url = url + item + "/"

            # Removing the Final /
            return url[:-1]
        return url + endpoints[0]


# pylint: disable=too-few-public-methods
class TMX:
    """Basic TMX Api Details

    :param protocol: The protocol to use for the api. Equal to
            "https"
    :type protocol: str
    :param base: The base url for the api. Equal to
            "trackmania.exchange"
    :type base: str
    :param api: The api endpoint for `trackmania.exchange`. Equal to
            "api".
    :type api: str

    """

    protocol: str = "https"
    base: str = "trackmania.exchange"
    api: str = "api"

    @staticmethod
    def build(endpoints: List[str]) -> str:
        """URL Builder for TMX API

        :param endpoints (: class:`List`[str]): The endpoints as a list.
        :param endpoints: List[str]:
        :returns: The URL.
        :rtype: str

        """
        url = f"{TMX.protocol}://{TMX.base}/{TMX.api}/"

        if len(endpoints) == 0:
            return url
        if len(endpoints) > 1:
            for item in endpoints:
                url = url + item + "/"

            # Removing the Final /
            return url[:-1]
        return url + endpoints[0]
