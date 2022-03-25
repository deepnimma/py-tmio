from redis import Redis

__all__ = ("Client",)

# pylint: disable=too-few-public-methods
class Client:
    """
    Client class to manage user defined constants

    Parameters
    ----------
    USER_AGENT : str
        The USER_AGENT to be used for the bot
    REDIS_HOST : str
        The host of the redis server
    REDIS_PORT : int
        The port of the redis server
    """

    USER_AGENT: str = None
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REMAINING_REQUESTS: int = None
