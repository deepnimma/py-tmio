# How to get a player's username from their ID
# There are 2 ways of doing this using py-tmio

from trackmania import Player


# 1st Way
async def run():
    player_data = Player.get("player id")


# 2nd Way
async def run():
    username = Player.get_username("player username")
