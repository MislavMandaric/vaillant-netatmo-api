"""Module containing a BaseClient for the Netatmo API."""

from __future__ import annotations

from typing import Awaitable, Callable

from authlib.integrations.httpx_client import AsyncOAuth2Client
from authlib.oauth2.rfc6749 import OAuth2Token

_API_HOST = "https://api.netatmo.com"
_TOKEN_PATH = "/oauth2/token"
_TOKEN_AUTH_METHOD = "client_secret_post"
_TOKEN_PLACEMENT = "body"


class BaseClient:
    """
    Base client for making HTTP requests to the Netatmo API.

    Uses AsyncOAuth2Client from authlib in the background to make authenticated requests. Should be used either as a singleton for making all requests to allow underlying httpx client to efficiently manage connection pool. Because of that, expected usage is to instantiate a client and store it in memory for the duration of the application that is using it. On application termination, the client should be gracefully shut down using the provioded async_close method, which will allow all pending requests to finish.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        scope: str | None = None,
        token: OAuth2Token | None = None,
        update_token: Callable[
            [OAuth2Token, str | None, str | None], Awaitable[None]
        ] = None,
    ) -> None:
        """
        Create new base client instance.

        Uses the provided parameters to instantiate the underlying AsyncOAuth2Client client.
        """

        self._client = AsyncOAuth2Client(
            client_id,
            client_secret,
            scope=scope,
            token=token,
            update_token=update_token,
            token_endpoint=_TOKEN_PATH,
            token_endpoint_auth_method=_TOKEN_AUTH_METHOD,
            token_placement=_TOKEN_PLACEMENT,
            base_url=_API_HOST,
        )

    async def async_close(self) -> None:
        """Close the underlying AsyncOAuth2Client client, allowing pending requests to finish."""

        await self._client.aclose()
