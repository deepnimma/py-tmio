from typing import Dict, List

from trackmania import Player, PlayerTrophies, TrophyLeaderboardPlayer

# There are no functions from `PlayerTrophies` that will give you an object of this class.
# The ONLY way you can get a `PlayerTrophies` object is by calling `Player.get_player()`.


async def run():
    player_data = await Player.get_player("UID")
    trophy_data = player_data.trophies

    # Get Trophy Gain / Loss History of a Player
    history = await trophy_data.history()

    # Get the Total Trophy Score of a player
    score = trophy_data.score()


# Getting Top Players based on trophies
async def top_trophies() -> List[TrophyLeaderboardPlayer]:
    return await PlayerTrophies.top()
