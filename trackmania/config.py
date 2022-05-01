import json
import logging
from contextlib import suppress
from datetime import datetime

import redis
from yarl import cache_clear

__all__ = ("Client",)

_log = logging.getLogger(__name__)


class Client:
    """
    .. versionadded:: 0.3.0

    Client class to manage user defined constants

    Parameters
    ----------
    USER_AGENT : str
        The USER_AGENT to be used for the bot.
    REDIS_HOST : str
        The host of the redis server.
    REDIS_PORT : int
        The port of the redis server.
    REDIS_DB : int
        The database of the redis server.
        .. versionadded:: 0.2.0
    REDIS_PASSWORD : str
        The password of the redis server.
        .. versionadded:: 0.2.0
    RATELIMIT_LIMIT: int
        The `trackmania.io` ratelimit limit.
        .. versionadded:: 0.2.1
    RATELIMIT_REMAINING : int
        The amount of remaining requests with `trackmania.io` api.
        .. versionadded:: 0.2.1
    RATELIMIT_RESET : datetime
        When the `trackmania.io` ratelimit will be reset. Date and Time in UTC
        .. versionadded :: 0.4.0
    """

    USER_AGENT: str = None
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = None

    RATELIMIT_LIMIT: int = 40
    RATELIMIT_REMAINING: int = None
    RATELIMIT_RESET: datetime = None

    redis_exceptions: tuple = (ConnectionRefusedError, redis.exceptions.ConnectionError)

    @staticmethod
    def _get_cache_client() -> redis.Redis:
        """
        Gets the Cache Client

        Returns
        -------
        :class:`redis.Redis`
            The cache_client
        """
        return redis.Redis(
            host=Client.REDIS_HOST,
            port=Client.REDIS_PORT,
            db=Client.REDIS_DB,
            password=Client.REDIS_PASSWORD,
        )


def get_from_cache(key: str) -> dict | None:
    """
    Gets a specific key from cache if it exists.
    Returns None if any value of that key does not exist.

    Parameters
    ----------
    key : str
        The key to check for.

    Returns
    -------
    dict
        The parsed data.
    """
    cache_client = Client._get_cache_client()

    with suppress(*Client.redis_exceptions):
        if cache_client.exists(key):
            _log.debug(f"Getting {key} from cache")
            try:
                return json.loads(cache_client.get(key).decode("utf-8"))
            except json.decoder.JSONDecodeError:
                return cache_client.get(key).decode("utf-8")
    return None


def set_in_cache(key: str, value: dict | str, ex: int = None) -> bool:
    """
    Set a key-value pair in cache with an expiration time of `ex`.

    Parameters
    ----------
    key : str
        The key for the cache.
    value : dict | str
        The value for the specific key.
    ex : int, optional
        The expiration time for the key-value pair. If None there is no expiration time, by default None

    Returns
    -------
    bool
        _description_
    """
    cache_client = Client._get_cache_client()

    with suppress(*Client.redis_exceptions):
        _log.debug(f"Setting {key} in cache with expiration time {ex}")
        if isinstance(value, str):
            return cache_client.set(name=key, value=value, ex=ex)
        elif isinstance(value, dict):
            return cache_client.set(name=key, value=json.dumps(value), ex=ex)

    return False


def cache_flushdb() -> None:
    """
    Flushes the entire db.
    DB is set in `Client` class.

    Returns
    -------
    bool
        True if successful, False if an error.
    """
    redis_client = Client._get_cache_client()

    try:
        return redis_client.flushdb(True)
    except Client.redis_exceptions:
        return False


def cache_flush_key(key: str) -> bool:
    """
    Flushes a specific key.

    Parameters
    ----------
    key : str
        The key to flush

    Returns
    -------
    bool
        Successful or Failure.
    """
    redis_client = Client._get_cache_client()

    try:
        redis_client.delete(key)
    except Client.redis_exceptions:
        return False

    return True
