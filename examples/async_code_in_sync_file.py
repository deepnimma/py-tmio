# This example shows you how to run asynchronous code in a normal python setting
import asyncio

from trackmania import Player

data = asyncio.run(Player.get_player("Some ID"))

# All examples assume the functions are being called from within other async functions
# If you are not running it in an async function, see above on how to run it.
