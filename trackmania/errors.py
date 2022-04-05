__all__ = (
    "TrackmaniaException",
    "TMIOException",
    "NoUserAgentSetError",
    "InvalidUsernameError",
    "InvalidIDError",
)


# pylint: disable=unnecessary-pass
class TrackmaniaException(Exception):
    """BASE exception class for py-tmio"""

    pass


class TMIOException(Exception):
    """BASE exception class for errors from trackmania.io"""

    pass


class InvalidPlayerException(TrackmaniaException):
    """ """

    def __init__(self, *args):
        if args:
            message = args[0]
        else:
            message = None

        super().__init__(message)


class NoUserAgentSetError(Exception):
    """ """

    def __init__(self):
        message = "No User Agent has been set.\nPlease read the README for instructions on how to set the USER_AGENT."
        super().__init__(message)


class InvalidUsernameError(InvalidPlayerException):
    """ """

    def __init__(self, *args):
        if args:
            message = args[0]
        else:
            message = None

        super().__init__(message)


class InvalidIDError(InvalidPlayerException):
    """ """

    def __init__(self, *args):
        if args:
            message = args[0]
        else:
            message = None

        super().__init__(message)


class InvalidMatchmakingGroupError(TrackmaniaException):
    """ """

    def __init__(self, *args):
        if args:
            message = args[0]
        else:
            message = None

        super().__init__(message)


class InvalidTrophyNumber(TrackmaniaException):
    """ """

    def __init__(self, *args):
        if args:
            message = args[0]
        else:
            message = None

        super().__init__(message)
