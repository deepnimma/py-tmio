# Examples

## TOC
1. [player](player.py)

### How to run asynchronous code in a synchronous function

```python
import asyncio
from trackmania import Player

def my_function():
    player_data = asyncio.run(Player.get_player("player_id"))

if __name__ == "__main__":
    my_function()
```