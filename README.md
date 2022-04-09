<div align=center>
<h1>py-trackmania.io</h1>

[![Trackmania.io API Status](https://img.shields.io/website?down_message=Offline&label=Trackmania.io%20API&up_message=Online&url=https%3A%2F%2Ftrackmania.io)](https://trackmania.io)
[![Pypi Version](https://img.shields.io/pypi/v/py-tmio?style=flat-square)](https://pypi.org/project/py-tmio)

[![GitHub issues](https://img.shields.io/github/issues/NottCurious/py-tmio?logo=github&style=flat-square)](https://github.com/NottCurious/py-tmio/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/NottCurious/py-tmio?logo=github&style=flat-square)](https://github.com/NottCurious/py-tmio/pulls)
[![GitHub Repo stars](https://img.shields.io/github/stars/NottCurious/py-tmio?logo=github&style=flat-square)](https://github.com/NottCurious/py-tmio/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/NottCurious/py-tmio?style=flat-square)](https://github.com/NottCurious/py-tmio/network/members)
[![Documentation Status](https://readthedocs.org/projects/py-trackmaniaio/badge/?version=latest&style=flat-square)](https://py-trackmaniaio.readthedocs.io/en/latest/?badge=latest)
[![Python Version](https://img.shields.io/pypi/pyversions/py-tmio?style=flat-square)](https://pypi.org/project/py-tmio)
[![Discord Server](https://img.shields.io/discord/962190413073088554?style=flat-square)](https://discord.gg/uFgjx5rEgr)

An Asyncio Friendly Trackmania API Wrapper for Python!
</div>

## Important - [Trackmania.io API for my own project?](https://openplanet.dev/tmio/api)

*See below on how to set your user agent*

Your User-Agent Must Have:

1. Your Discord Username
2. Your Project Name

Example:
`NottCurious#4351 | TMIndiaBot`

*" | via py-tmio" is automatically appended to your user agent*

#### How to set user agent.

```python
from trackmania import Client

Client.USER_AGENT = "NottCurious#4351 | TMIndiaBot"
```

#### How to set Redis Server Settings

```python
from trackmania import Client

Client.REDIS_HOST = "127.0.0.1" # 127.0.0.1 is default
Client.REDIS_PORT = 6379 # 6379 is default
Client.REDIS_DB = 0 # 0 is default
Client.REDIS_PASSWORD = "yadayadayada" # Defaults to None. Don't need to change this if your redis server does not have a password.
```

## Support Server

You can report bug fixes, issues, feature request or ask for help at the discord server! (Click the Badge!)


[![Discord Server](https://img.shields.io/discord/962190413073088554?style=flat-square)](https://discord.gg/uFgjx5rEgr)

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


## Pull Requests and Issues

If you have any suggestions, bugs, fixes or enhancements, please open
a [Pull Request](https://github.com/NottCurious/py-tmio/compare)
or [Issue](https://github.com/NottCurious/py-tmio/issues/new)

## Discord

Contact me on Discord if you have any questions, NottCurious#4351

Or join the [support server here!](https://discord.gg/uFgjx5rEgr)

## License

[MIT License](https://mit-license.org/)
