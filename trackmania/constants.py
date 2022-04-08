from typing import List


class _TMIOTabs:
    """
    .. versionadded:: 0.3.0

    _TMIO Endpoints
    """

    def __init__(self):
        self.PLAYER: str = "player"
        self.PLAYERS: str = "players"
        self.TROPHIES: str = "trophies"
        self.MAP: str = "map"
        self.LEADERBOARD: str = "leaderboard"
        self.MATCHES: str = "matches"

        self.TOP_MATCHMAKING: str = "top/matchmaking/2"
        self.TOP_ROYAL: str = "top/matchmaking/3"
        self.TOP_TROPHIES: str = "top/trophies"

        self.MATCHMAKING_ID: int = 2
        self.ROYAL_ID: int = 3

        self.TOTD: str = "totd"
        self.COTD: str = "cotd"
        self.ADS: str = "ads"


class _TMIO:
    """
    .. versionadded:: 0.3.0

    Basic _TMIO Api Details

    Parameters
    ----------
    PROTOCOL : str
        The PROTOCOL to use for the api. Equal to "https"
    BASE : str
        The BASE url for the api. Equal to "trackmania.io"
    api : str
        The api endpoint for `trackmania.io`. Equal to "api".
    TABS : :class:`_TMIOTabs`
        The TABS for the api.
    """

    PROTOCOL: str = "https"
    BASE: str = "trackmania.io"
    API: str = "api"

    TABS: _TMIOTabs = _TMIOTabs()

    @staticmethod
    def build(endpoints: List[str]) -> str:
        """Builds a _TMIO endpoint url.

        Parameters
        ----------
        endpoints : List[str]
            The endpoints to build the url with.

        Returns
        -------
        str
            The built endpoint url.

        """
        url = f"{_TMIO.PROTOCOL}://{_TMIO.BASE}/{_TMIO.API}/"

        if len(endpoints) == 0:
            return url
        if len(endpoints) > 1:
            for item in endpoints:
                if isinstance(item, int):
                    item = str(item)
                url = url + item + "/"

            # Removing the Final /
            return url[:-1]
        return url + endpoints[0]


class _TMX:
    """
    .. versionadded:: 0.3.0

    Basic _TMX Api Details

    Parameters
    ----------
    PROTOCOL : str
        The PROTOCOL to use for the api. Equal to "https"
    BASE : str
        The BASE url for the api. Equal to "trackmania.exchange"
    api : str
        The api endpoint for `trackmania.exchange`. Equal to "api".

    """

    PROTOCOL: str = "https"
    BASE: str = "trackmania.exchange"
    API: str = "api"

    @staticmethod
    def build(endpoints: List[str]) -> str:
        """URL Builder for _TMX API

        Parameters
        ----------
        endpoints : class:`List`[str]
            The endpoints as a list.

        Returns
        -------
        str
            The URL.
        """
        url = f"{_TMX.PROTOCOL}://{_TMX.BASE}/{_TMX.API}/"

        if len(endpoints) == 0:
            return url
        if len(endpoints) > 1:
            for item in endpoints:
                if isinstance(item, int):
                    item = str(item)
                url = url + item + "/"

            # Removing the Final /
            return url[:-1]
        return url + endpoints[0]
