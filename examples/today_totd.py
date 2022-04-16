# An example to show how to get the latest TOTDs data
# From both Trackmania.io and TMX
import asyncio
from datetime import datetime

from trackmania import TOTD, Client, TMXMap, totd

# Set your Client User Agent
Client.USER_AGENT = "Testing Agent | DiscordUsernaem#1234"


async def run():
    # There are 2 ways to get the latest totd data

    # Way 1
    # Using the latest_totd command
    totd_data: TOTD = await TOTD.latest_totd()

    # Way 2
    # Using the get_totd command
    totd_data: TOTD = await TOTD.get_totd(datetime.utcnow())

    # Both the above commands do the exact same thing, the exact same way
    # Use based on your needs.

    # All Parameters
    print(totd_data.campaign_id)  # int, The campaign's id
    print(totd_data.leaderboard_uid)  # int, The leaderboard's uid
    print(totd_data.month_day)  # int, The day of the month the TOTD was on.
    print(totd_data.week_day)  # int, The day of the week the TOTD was on.

    print(
        totd_data.map
    )  # Map object, Check documentation for all functions related to this class.

    tmx_code: int = totd_data.map.exchange_id  # Can be None if the map is not on TMX

    # Getting TMX Map Data
    tmx_map_data = await TMXMap.get_map(int(tmx_code))

    # Check documentation for all functions related to this class.


# Running the Function
if __name__ == "__main__":
    asyncio.run(run())
