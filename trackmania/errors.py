"""
MIT License

Copyright (c) 2022-present Deepesh Nimma

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

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
