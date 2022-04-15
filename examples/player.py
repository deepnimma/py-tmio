from typing import List

from trackmania import Player
from trackmania.player import PlayerSearchResult


# Getting a player's player id from username
async def get_player_id(username: str) -> str:
    return await Player.get_id(username)


# Getting a player's username from player id
async def get_username(player_id: str) -> str:
    return await Player.get_username(player_id)


# Getting a player's data from player id
async def get_data(player_id: str) -> str:
    return await Player.get_player(player_id)


# Search for players with a given name
async def search_player(username: str) -> List[PlayerSearchResult]:
    return await Player.search_player(username)
