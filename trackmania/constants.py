"""
MIT License

Copyright (c) 2022-present Deepesh Nimma

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
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
    """
    Basic TMIO Api Details

    Parameters
    ----------
    protocol : str
        The protocol to use for the api. Equal to "https"
    base : str
        The base url for the api. Equal to "trackmania.io"
    api : str
        The api endpoint for `trackmania.io`. Equal to "api".
    tabs : class:`TMIOTabs`
        The tabs for the api.

    Returns
    -------

    """

    protocol: str = "https"
    base: str = "trackmania.io"
    api: str = "api"

    tabs: TMIOTabs = TMIOTabs()

    @staticmethod
    def build(endpoints: List[str]) -> str:
        """
        Builds a TMIO endpoint url.

        Parameters
        ----------
        endpoints : List[str]
            The endpoints to build the url with.
        endpoints: List[str] :
            

        Returns
        -------
        str
            The built endpoint url.

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
    """
    Basic TMX Api Details

    Parameters
    ----------
    protocol : str
        The protocol to use for the api. Equal to "https"
    base : str
        The base url for the api. Equal to "trackmania.exchange"
    api : str
        The api endpoint for `trackmania.exchange`. Equal to "api".

    Returns
    -------

    """

    protocol: str = "https"
    base: str = "trackmania.exchange"
    api: str = "api"

    @staticmethod
    def build(endpoints: List[str]) -> str:
        """
        URL Builder for TMX API

        Parameters
        ----------
        endpoints : class:`List`[str]
            The endpoints as a list.
        endpoints: List[str] :
            

        Returns
        -------
        str
            The URL.

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
