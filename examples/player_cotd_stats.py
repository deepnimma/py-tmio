# An example to show how to get a player's cotd stats
import asyncio

from trackmania import Client, Player, PlayerCOTD
from trackmania.cotd import PlayerCOTDStats

# Set your Client User Agent
Client.USER_AGENT = "Testing Agent | DiscordUsernaem#1234"


async def run():
    # Get a player's id
    player_id = await Player.get_id("USERNAME")

    # Get a player's cotd stats
    player_cotd_stats = await PlayerCOTD.get_page(player_id)

    # All Parameters
    print(player_cotd_stats.player_id)  # int, The player's id

    # Loop through recent 25 results.
    for result in player_cotd_stats.recent_results:
        print(result.name)

    # Stats
    stats: PlayerCOTDStats = player_cotd_stats.stats
    # Check documentation for all functions related to `PlayerCOTDStats` class.


# Running the Function
if __name__ == "__main__":
    asyncio.run(run())
