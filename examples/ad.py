import imp
from typing import List

from trackmania import Ad


# List all ads currently in Trackmania2020
async def list_all_ads() -> List[Ad]:
    return await Ad.list_ads()


# Get a specific ad by its id
async def get_an_ad() -> Ad | None:
    return await Ad.get_ad("UID")  # Ad | None
