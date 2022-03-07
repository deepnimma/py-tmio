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
from typing import Optional

import aiohttp

from .config import Client
from .errors import NoUserAgentSetError

__all__ = ("ResponseCodeError", "APIClient")


class ResponseCodeError(ValueError):
    """Raised when a non-OK HTTP Response is received

    :param response: The response object
    :type response: aiohttp.ClientResponse
    :param response_json: The response json
    :type response_json: dict
    :param response_text: The response text
    :type response_text: str
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
    API Wrappers
    """

    def __init__(self, **session_kwargs):
        if Client.user_agent is None:
            raise NoUserAgentSetError()

        self.session = aiohttp.ClientSession(
            headers={"User-Agent": Client.user_agent + " | via py-tmio"},
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
        self, method: str, endpoint: str, *, raise_for_status: bool = True, **kwargs
    ) -> dict:
        """Send an HTTP request to the site API and return the JSON response."""
        async with self.session.request(method.upper(), endpoint, **kwargs) as resp:
            await self.maybe_raise_for_status(resp, raise_for_status)
            return await resp.json()

    async def get(
        self, endpoint: str, *, raise_for_status: bool = True, **kwargs
    ) -> dict:
        """Site API GET."""
        return await self.request(
            "GET", endpoint, raise_for_status=raise_for_status, **kwargs
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
