from redis import Redis

__all__ = ("Client",)


# pylint: disable=too-few-public-methods
class Client:
    """
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
    REDIS_PASSWORD : str
        The password of the redis server.
    RATELIMIT_LIMIT: int
        The `trackmania.io` ratelimit limit.
    RATELIMIT_REMAINING : int
        The amount of remaining requests with `trackmania.io` api.
    """

    USER_AGENT: str = None
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = None

    RATELIMIT_LIMIT: int = 40
    RATELIMIT_REMAINING: int = None
