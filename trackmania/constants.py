from typing import List

from typing_extensions import Self


class _TMIOTabs:
    """
    .. versionadded:: 0.3.0

    TMIO Endpoints
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

    Basic TMIO Api Details

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

    @classmethod
    def build(cls: Self, endpoints: List[str]) -> str:
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
        url = f"{cls.PROTOCOL}://{cls.BASE}/{cls.API}/"

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


class _TMXTabs:
    """
    .. versionadded :: 0.3.3

    TMX Endpoints
    """

    def __init__(self):
        self.MAPS = "maps"
        self.GET_MAP_INFO = "get_map_info"
        self.GET_TRACK_INFO = "get_track_info"
        self.MULTI = "multi"
        self.ID = "id"


class _TMX:
    """
    .. versionadded:: 0.3.0

    Basic TMX Api Details

    Parameters
    ----------
    PROTOCOL : str
        The PROTOCOL to use for the api. Equal to "https"
    BASE : str
        The BASE url for the api. Equal to "trackmania.exchange"
    api : str
        The api endpoint for `trackmania.exchange`. Equal to "api".
    TABS: :class:`_TMXTabs`
        .. versionadded :: 0.3.3
        The TABS for TMX API
    """

    PROTOCOL: str = "https"
    BASE: str = "trackmania.exchange"
    API: str = "api"
    TABS: _TMXTabs = _TMXTabs()

    MAP_TYPE_ENUMS: dict = {
        1: "Race",
        2: "FullSpeed",
        3: "Tech",
        4: "RPG",
        5: "LOL",
        6: "Press Forward",
        7: "SpeedTech",
        8: "MultiLap",
        9: "Offroad",
        10: "Trial",
        11: "ZrT",
        12: "SpeedFun",
        13: "Competitive",
        14: "Ice",
        15: "Dirt",
        16: "Stunt",
        17: "Reactor",
        18: "Platform",
        19: "Slow Motion",
        20: "Bumper",
        21: "Fragile",
        22: "Scenery",
        23: "Kacky",
        24: "Endurance",
        25: "Mini",
        26: "Remake",
        27: "Mixed",
        28: "Nascar",
        29: "SpeedDrift",
        30: "Minigame",
        31: "Obstacle",
        32: "Transitional",
        33: "Grass",
        34: "Backwards",
        35: "Freewheel",
        36: "Signature",
        37: "Royal",
        38: "Water",
        39: "Plastic",
        40: "Arena",
    }

    @classmethod
    def build(cls: Self, endpoints: List[str]) -> str:
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
        url = f"{cls.PROTOCOL}://{cls.BASE}/{cls.API}/"

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
