from redis import Redis

__all__ = ("Client",)

# pylint: disable=too-few-public-methods
class Client:
    """Client class to manage user defined constants

    Parameters
    ----------
    user_agent : str
        The user_agent to be used for the bot
    redis_host : str
        The host of the redis server
    redis_port : int
        The port of the redis server

    Returns
    -------

    """

    user_agent = None
    redis_host = "127.0.0.1"
    redis_port = 6379
