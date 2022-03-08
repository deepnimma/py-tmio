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
import json
from typing import List

import redis

from trackmania.structures.player import PlayerSearchResult

from ..api import APIClient
from ..config import cache_client
from ..constants import TMIO
from ..errors import InvalidIDError, InvalidMatchmakingGroupError, InvalidUsernameError
from ..structures.player import Player
from ..util.player_parsers import PlayerParsers

__all__ = ("PlayerManager",)


class PlayerManager:
    """
    PlayerManager is a class that handles all player related functions.
    """

    @staticmethod
    async def get(player_id: str) -> Player:
        """
        Retrieves a player's information

        :param player_id: The player id to get information for.
        :type player_id: str
        :raises InvalidIDError: if the player id is empty, or no player exists with that player_id.
        :return: The player's information.
        :rtype: :class:`Player`

        Caching
        -------
        * Caches the player information for 10 minutes.
        * Caches `username:player_id` pair forever.
        * Caches `player_id:username` pair forever.
        """

        if player_id == "":
            raise InvalidIDError("Player ID cannot be empty")

        try:
            # Checking the cache to see if the player is already in the cache
            response = cache_client.get(name=f"{player_id}|Data")
        except (ConnectionRefusedError, redis.exceptions.ConnectionError):
            # User does not have redis running
            response = None

        # Response is None when it is not in the cache
        if response is None:
            api_client = APIClient()

            player_url = TMIO.build([TMIO.tabs.player, player_id])

            response = await api_client.get(player_url)
            await api_client.close()

            try:
                raise InvalidIDError(response["error"])
            except KeyError:
                pass
        else:
            response = json.loads(response)

        (
            club_tag,
            first_login,
            player_id,
            last_club_tag_change,
            login,
            meta,
            name,
            trophies,
            zone,
            m3v3,
            royal,
        ) = PlayerParsers.parse_data(response)

        try:
            # Stores the Player's ID Forever
            # cache_client.set(key=f'{name.lower()}|ID', value=player_id, expire=0)
            cache_client.set(name=f"{name.lower()}|ID", value=player_id)

            # Stores the Player's Username-ID Pair Forever
            cache_client.set(name=f"{player_id}|username", value=name)

            # Stores the Player Object for 10 minutes
            cache_client.set(
                name=f"{player_id}|Data", value=json.dumps(response), ex=600
            )
        except (ConnectionRefusedError, redis.exceptions.ConnectionError):
            pass

        return Player(
            club_tag,
            first_login,
            player_id,
            last_club_tag_change,
            login,
            meta,
            name,
            trophies,
            zone,
            m3v3,
            royal,
        )

    @staticmethod
    async def search(
        username: str,
    ) -> None | PlayerSearchResult | List[PlayerSearchResult]:
        """
        Searches for a player's information

        :param username: The player's username to search for.
        :type username: str
        :raises InvalidUsernameError: If the username is empty or if there is no users with this username.
        :return: None if no players. PlayerSearchResult if one player. List of PlayerSearchResult if multiple players.
        :rtype: None|PlayerSearchResult|List[PlayerSearchResult]
        """
        if username == "":
            raise InvalidUsernameError("Username cannot be empty.")

        api_client = APIClient()

        player_url = TMIO.build([TMIO.tabs.players]) + f"/find?search={username}"

        response = await api_client.get(player_url)
        await api_client.close()

        try:
            raise InvalidUsernameError(response["error"])
        except (KeyError, TypeError):
            pass

        if len(response) == 0:
            return None
        if len(response) == 1:
            (
                club_tag,
                name,
                player_id,
                zones,
                threes,
                royal,
            ) = PlayerParsers._parse_search_results(response[0])

            return PlayerSearchResult(club_tag, name, player_id, zones, threes, royal)

        results = []

        for player in response:
            (
                club_tag,
                name,
                player_id,
                zones,
                threes,
                royal,
            ) = PlayerParsers._parse_search_results(player)

            results.append(
                PlayerSearchResult(club_tag, name, player_id, zones, threes, royal)
            )

        return results

    @staticmethod
    async def to_account_id(username: str) -> str | None:
        """
        Returns the account id of the given username

        :param username: The username of the player.
        :type username: str
        :return: The id of the player.
        :rtype: str | None

        Caching
        -------
        * Caches `username:player_id` pair forever.
        * Caches `player_id:username` pair forever.
        """
        try:
            player_id = cache_client.get(name=f"{username.lower()}|ID")
        except (ConnectionRefusedError, redis.exceptions.ConnectionError):
            player_id = None

        if player_id is not None:
            return player_id

        players = await PlayerManager.search(username)

        if players is None:
            return None
        if isinstance(players, PlayerSearchResult):
            try:
                cache_client.set(
                    name=f"{players.name.decode('utf-8').lower()}|ID",
                    value=players.player_id,
                )
                cache_client.set(
                    name=f"{players.player_id.decode('utf-8')}|username",
                    value=players.name,
                )
            except (ConnectionRefusedError, redis.exceptions.ConnectionError):
                pass
            return players.player_id
        # Cache all players in the list.
        for player in players:
            try:
                cache_client.set(
                    name=f"{player.name.lower()}|ID", value=player.player_id
                )
                cache_client.set(name=f"{player.player_id}|username", value=player.name)
            except (ConnectionRefusedError, redis.exceptions.ConnectionError):
                pass

        return players[0].player_id

    @staticmethod
    async def to_username(player_id: str) -> str | None:
        """
        Gets a player's username from their ID.

        :param player_id: The ID of the player.
        :type player_id: str
        :return: The player's username, None if the player does not exist.
        :rtype: str | None
        """

        try:
            username = cache_client.get(name=f"{player_id}|username")
        except (ConnectionRefusedError, redis.exceptions.ConnectionError):
            username = None

        if username is not None:
            return username

        player = await PlayerManager.get(player_id)
        return player.name

    @staticmethod
    async def top_matchmaking(group: int, page: int = 0):
        """
        Retrieves the Matchmaking leaderboard.

        :param group: The group id, 2 is 3v3 matchmaking and 3 is royal matchmaking.
        :type group: int
        :param page: The page of the leaderboard. Each number is 50 users, defaults to 0
        :type page: int, optional

        Caching
        -------
        Caches each page for 1 hour.
        """
        try:
            leaderboard = cache_client.get(name=f"matchmaking|{group}|{page}")
        except (ConnectionRefusedError, redis.exceptions.ConnectionError):
            leaderboard = None

        if leaderboard is not None:
            return leaderboard

        api_client = APIClient()

        if int(group) not in (2, 3):
            raise InvalidMatchmakingGroupError(
                "Matchmaking Group should be 2 or 3. 2 for 3v3, 3 for royal"
            )

        leaderboard_url = TMIO.build([TMIO.tabs.top_matchmaking, group, page])

        leaderboard_data = await api_client.get(leaderboard_url)

        await api_client.close()

        try:
            cache_client.set(
                name=f"matchmaking|{group}|{page}", value=leaderboard_data, ex=3600
            )
        except (ConnectionRefusedError, redis.exceptions.ConnectionError):
            pass

        return leaderboard_data

    @staticmethod
    async def top_trophies(page: int = 0):
        """
        Gets the Trophy leaderboard.

        :param page: Page for the leaderboard, each page contains 50 players. defaults to 0
        :type page: int, optional

        Caching
        -------
        Caches trophy leaderboard page for 3 hr
        """
        try:
            leaderboard = cache_client.get(name=f"trophy|{page}")
        except (ConnectionRefusedError, redis.exceptions.ConnectionError):
            leaderboard = None

        if leaderboard is not None:
            return leaderboard

        api_client = APIClient()

        trophy_leaderboard_url = TMIO.build([TMIO.tabs.top_trophies, page])

        leaderboard_data = await api_client.get(trophy_leaderboard_url)
        await api_client.close()

        try:
            cache_client.set(name=f"trophy|{page}", value=leaderboard_data, ex=10800)
        except (ConnectionRefusedError, redis.exceptions.ConnectionError):
            pass

        return leaderboard_data
