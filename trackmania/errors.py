__all__ = (
    "TrackmaniaException",
    "TMIOException",
    "InvalidPlayerException",
    "NoUserAgentSetError",
    "InvalidUsernameError",
    "InvalidIDError",
    "InvalidTrophyNumber",
    "InvalidTOTDDate",
)


# pylint: disable=unnecessary-pass
class TrackmaniaException(Exception):
    """BASE exception class for py-tmio"""

    pass


class TMIOException(Exception):
    """BASE exception class for errors from trackmania.io"""

    pass


class TMXException(Exception):
    """BASE exception class for errors from trackmania.exchange"""

    pass


class InvalidPlayerException(TrackmaniaException):
    """Base Exception class for Player-Related exceptions"""

    pass


class NoUserAgentSetError(Exception):
    """Raised when a User-Agent is not set."""

    def __init__(self):
        message = "No User Agent has been set.\nPlease read the README for instructions on how to set the USER_AGENT."
        super().__init__(message)


class InvalidUsernameError(InvalidPlayerException):
    """Raised when a username is not valid."""

    def __init__(self, *args):
        if args:
            message = args[0]
        else:
            message = None

        super().__init__(message)


class InvalidIDError(InvalidPlayerException):
    """Raised when an Invalid ID is given."""

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


class InvalidTOTDDate(TrackmaniaException):
    """Raised when an invalid TOTD Date is given."""

    def __init__(self, *args):
        if args:
            message = args[0]
        else:
            message = None

        super().__init__(message)


class InvalidTMXCode(TMXException):
    """Raised when an invalid TMX Code is given."""

    def __init__(self, *args):
        if args:
            message = args[0]
        else:
            message = None

        super().__init__(message)
