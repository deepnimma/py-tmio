from redis import Redis

__all__ = ("Client",)

# pylint: disable=too-few-public-methods
class Client:
    """Client class to manage user defined constants

    :param user_agent: The user_agent to be used for the bot
    :type user_agent: str
    :param redis_host: The host of the redis server
    :type redis_host: str
    :param redis_port: The port of the redis server
    :type redis_port: int

    """

    user_agent = None
    redis_host = "127.0.0.1"
    redis_port = 6379
