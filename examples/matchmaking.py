from typing import Dict, List

from trackmania import Player, PlayerMatchmaking

# There are no functions from `PlayerMatchmaking` that will give you an object of this class.

# Get Matchmaking History of a Player
async def matchmaking_history() -> List[Dict]:
    player_data: Player = Player.get_player("PLAYER ID")

    threes = player_data.m3v3_data
    royal = player_data.royal_data

    threes_history = await threes.history()
    royal_history = await royal.history()

    return threes_history, royal_history


# Get Top Matchmaking Leaderboard Data
async def top_matchmaking() -> List[Dict]:
    # For normal 3v3 matchmaking
    return await PlayerMatchmaking.top_matchmaking(
        royal=False
    )  # For royal matchmaking leaderboard, set the `royal` parameter to `True`
