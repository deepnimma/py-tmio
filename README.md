<div align=center>
<h1>py-trackmania.io</h1>

[![Trackmania.io API Status](https://img.shields.io/website?down_message=Offline&label=Trackmania.io%20API&up_message=Online&url=https%3A%2F%2Ftrackmania.io)](https://trackmania.io)

[![GitHub issues](https://img.shields.io/github/issues/NottCurious/py-tmio?logo=github)](https://github.com/NottCurious/py-tmio/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/NottCurious/py-tmio?logo=github)](https://github.com/NottCurious/py-tmio/pulls)
[![GitHub Repo stars](https://img.shields.io/github/stars/NottCurious/py-tmio?logo=github&style=flat-square)](https://github.com/NottCurious/py-tmio/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/NottCurious/py-tmio?style=flat-square)](https://github.com/NottCurious/py-tmio/network/members)

An Asyncio Friendly Trackmania API Wrapper for Python!
</div>

## Important - [Trackmania.io API for my own project?](https://openplanet.dev/tmio/api)
*See below on how to set your user_agent*

Your User-Agent Must Have:
1. Your Discord Username
2. Your Project Name

Example:
`NottCurious#4351 | TMIndiaBot`

*" | via py-tmio" is automatically appended to your user_agent*

#### How to set user_agent
```python
from trackmania import Client

Client.user_agent = "NottCurious#4351 | TMIndiaBot"
```

#### How to set Redis Server host and port
```python
from trackmania import Client

Client.redis_host = "127.0.0.1"
Client.redis_port = 6379
```

## Docs
Docs can be found on [readthedocs.org](https://py-trackmaniaio.readthedocs.io/en/latest/).

## Installation
**Note:** Must have Python 3.10 or higher.
```shell
python3 -m pip install py-tmio # Linux

python -m pip install py-tmio # Windows
```

## Caching
Caching is done using a redis server. The client defaults to `127.0.0.1:6379`.

Caching is not *required* but is highly recommended.

## Changelog
**v0.1.0**

<small>**15th March, 2022**</small>
* First Beta Release of py-tmio
* `player_manager`
    * `get_player(player_id)` command
    * `search_player(username)` command
    * `to_account_id(username)` command
    * `to_username(account_id)` command
    * `top_matchmaking(group, page)` command
    * `top_trophies(page)` command
* `ad_manager`
    * `get_ad(ad_id)` command
* `totd_manager`
    * `latest_totd(leaderboard)` command
    * `totd(year, month, day, leaderboard)` command

## Examples
### Latest TOTD
```python
from trackmania.managers import totd_manager

# In Async Function
latest_totd = await totd_manager.latest_totd()

print(latest_totd.map_name)
```

## Pull Requests and Issues
If you have any suggestions, bugs, fixes or enhancements, please open a [Pull Request](https://github.com/NottCurious/py-tmio/compare) or [Issue](https://github.com/NottCurious/py-tmio/issues/new)

## Discord
Contact me on Discord if you have any questions, NottCurious#4351

## License
[MIT License](https://mit-license.org/)
