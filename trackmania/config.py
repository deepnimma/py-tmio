from datetime import datetime

import redis

__all__ = ("Client",)


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
    except (ConnectionRefusedError, redis.exceptions.ConnectionError):
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
    except (ConnectionRefusedError, redis.exceptions.ConnectionError):
        return False

    return True
