"""Module containing an AuthClient for the Netatmo API."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from authlib.oauth2.rfc6749 import OAuth2Token

from .base import BaseClient


@asynccontextmanager
async def auth_client(
    client_id: str,
    client_secret: str,
    scope: str,
) -> AsyncGenerator[AuthClient, None]:
    client = AuthClient(client_id, client_secret, scope)

    try:
        yield client
    finally:
        await client.async_close()

class AuthClient(BaseClient):
    """
    Client for making HTTP requests to the Netatmo API. Used for the subset of the API related to the authentication: getting the access and refresh tokens.

    Uses BaseClient as a basis for making HTTP requests.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        scope: str,
    ) -> None:
        """
        Create new auth client instance.

        Uses the provided parameters to instantiate the underlying AsyncOAuth2Client client from the BaseClient class.
        """

        super().__init__(
            client_id,
            client_secret,
            scope=scope,
        )

    async def async_get_token(
        self,
        username: str,
        password: str,
        user_prefix: str,
        app_version: str,
    ) -> OAuth2Token:
        """
        Get the access and refresh tokens from the Netatmo API which can be used for making requests towards all other protected APIs. Uses the resource owner password credentials grant, with custom Vaillant parameters - user prefix and app version.

        Returns an OAuth token object containing access and refresh tokens.
        """

        return await self._client.fetch_token(
            username=username,
            password=password,
            user_prefix=user_prefix,
            app_version=app_version,
        )
