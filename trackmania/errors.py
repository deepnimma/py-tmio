__all__ = (
    "TrackmaniaException",
    "NoUserAgentSetError",
    "InvalidUsernameError",
    "InvalidIDError",
)


# pylint: disable=unnecessary-pass
class TrackmaniaException(Exception):
    """Base exception class for py-tmio"""

    pass


class InvalidPlayerException(TrackmaniaException):
    """Exception raised when an invalid player is found."""

    def __init__(self, *args):
        if args:
            message = args[0]
        else:
            message = None

        super().__init__(message)


class NoUserAgentSetError(Exception):
    """Exception raised when no user_agent has been set"""

    def __init__(self):
        message = "No User Agent has been set.\nPlease read the README for instructions on how to set the user_agent."
        super().__init__(message)


class InvalidUsernameError(InvalidPlayerException):
    """Exception raised when an invalid username has been passed as an argument."""

    def __init__(self, *args):
        if args:
            message = args[0]
        else:
            message = None

        super().__init__(message)


class InvalidIDError(InvalidPlayerException):
    """Exception raised when an invalid ID has been passed as an argument."""

    def __init__(self, *args):
        if args:
            message = args[0]
        else:
            message = None

        super().__init__(message)


class InvalidMatchmakingGroupError(TrackmaniaException):
    """Exception raised when an invalid matchmaking group has been passed as an argument."""

    def __init__(self, *args):
        if args:
            message = args[0]
        else:
            message = None

        super().__init__(message)


class InvalidTrophyNumber(TrackmaniaException):
    """Exception raised when an invalid trophy number has been passed as an argument."""

    def __init__(self, *args):
        if args:
            message = args[0]
        else:
            message = None

        super().__init__(message)
