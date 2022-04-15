# Example to show how to get a player's data
import asyncio

from trackmania import Player


async def run():
    player_data = await Player.get_player("some id")
