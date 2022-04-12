# Example to show how to get a player's data
import asyncio

from trackmania import Player


# If in async function
async def run():
    player_data = await Player.get("Some ID")


# If in normal function
def run():
    player_data = asyncio.run(Player.get("Some ID"))
