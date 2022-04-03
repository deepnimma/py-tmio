import logging
from typing import Optional

import aiohttp

from .config import Client
from .errors import NoUserAgentSetError

__all__ = ("ResponseCodeError", "APIClient")
_log = logging.getLogger(__name__)


class ResponseCodeError(ValueError):
    """
    .. versionadded:: 0.1.0

    Raised when a non-OK HTTP Response is received

    Parameters
    ----------
    response : :class:`aiohttp.ClientResponse`
        The response object
    response_json : :class:`Dict`
        The response json
    response_text : str
        The response text

    """

    def __init__(
        self,
        response: aiohttp.ClientResponse,
        response_json: Optional[dict] = None,
        response_text: str = "",
    ):
        super().__init__(response_text)
        self.status = response.status
        self.response_json = response_json or {}
        self.response_text = response_text
        self.response = response

    def __str__(self):
        response = self.response_json if self.response_json else self.response_text
        return f"Status: {self.status} Response: {response}"


# pylint: disable=W0612
class APIClient:
    """
    .. versionadded:: 0.1.0

    API Wrappers
    """

    def __init__(self, **session_kwargs):
        if Client.USER_AGENT is None:
            raise NoUserAgentSetError()

        self.session = aiohttp.ClientSession(
            headers={"User-Agent": Client.USER_AGENT + " | via py-tmio"},
            **session_kwargs,
        )

    async def close(self) -> None:
        """
        Close the AIOHTTP Session
        """

        await self.session.close()

    # pylint: disable=R0201
    async def maybe_raise_for_status(
        self, response: aiohttp.ClientResponse, should_raise: bool
    ) -> None:
        """Raise ResponseCodeError for non-OK response if an exception should be raised"""
        if should_raise and response.status >= 400:
            try:
                response_json = await response.json()
                raise ResponseCodeError(response=response, response_json=response_json)
            except aiohttp.ContentTypeError as content_type_error:
                response_text = await response.text()
                raise ResponseCodeError(
                    response=response, response_text=response_text
                ) from content_type_error

    async def request(
        self,
        method: str,
        endpoint: str,
        *,
        raise_for_status: bool = True,
        **kwargs,
    ) -> dict:
        """Send an HTTP request to the site API and return the JSON response."""
        async with self.session.request(method.upper(), endpoint, **kwargs) as resp:
            await self.maybe_raise_for_status(resp, raise_for_status)
            _log.info(f"Sending {method.upper()} to {endpoint}")
            try:
                if "trackmania.io" in endpoint:
                    Client.RATELIMIT_LIMIT = int(
                        resp.headers.get("x-ratelimit-limit")[0]
                    )
                    Client.RATELIMIT_REMAINING = int(
                        resp.headers.get("x-ratelimit-remaining")[0]
                    )
            except (AttributeError, TypeError):
                pass
            return await resp.json()

    async def get(
        self,
        endpoint: str,
        *,
        raise_for_status: bool = True,
        **kwargs,
    ) -> dict:
        """Site API GET."""
        return await self.request(
            "GET",
            endpoint,
            raise_for_status=raise_for_status,
            **kwargs,
        )

    async def patch(
        self, endpoint: str, *, raise_for_status: bool = True, **kwargs
    ) -> dict:
        """Site API PATCH."""
        return await self.request(
            "PATCH", endpoint, raise_for_status=raise_for_status, **kwargs
        )

    async def post(
        self, endpoint: str, *, raise_for_status: bool = True, **kwargs
    ) -> dict:
        """Site API POST."""
        return await self.request(
            "POST", endpoint, raise_for_status=raise_for_status, **kwargs
        )

    async def put(
        self, endpoint: str, *, raise_for_status: bool = True, **kwargs
    ) -> dict:
        """Site API PUT."""
        return await self.request(
            "PUT", endpoint, raise_for_status=raise_for_status, **kwargs
        )
