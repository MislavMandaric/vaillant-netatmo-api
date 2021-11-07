"""Module containing an AuthClient for the Netatmo API."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Callable

from httpx import AsyncClient

from .base import BaseClient
from .token import Token, TokenStore

_TOKEN_PATH = "oauth2/token"


@asynccontextmanager
async def auth_client(
    client_id: str,
    client_secret: str,
    on_token_update: Callable[[Token], None],
) -> AsyncGenerator[AuthClient, None]:
    client = AsyncClient()
    token_store = TokenStore(client_id, client_secret, None, on_token_update)
    
    c = AuthClient(client, token_store)

    try:
        yield c
    finally:
        await client.aclose()

class AuthClient(BaseClient):
    """
    Client for making HTTP requests to the Netatmo API. Used for the subset of the API related to the authentication: getting the access and refresh tokens.

    Uses BaseClient as a basis for making HTTP requests.
    """

    def __init__(
        self,
        client: AsyncClient,
        token_store: TokenStore,
    ) -> None:
        """
        Create new auth client instance.

        Uses the provided parameters to instantiate the BaseClient class.
        """

        self._token_store = token_store
        super().__init__(client, None)

    async def async_token(
        self,
        username: str,
        password: str,
        user_prefix: str,
        app_version: str,
    ) -> None:
        """
        Get the access and refresh tokens from the Netatmo API which can be used for making requests towards all other protected APIs. Uses the resource owner password credentials grant, with custom Vaillant parameters - user prefix and app version.

        On success, returns nothing. On error, throws an exception.
        """

        data = {
            "username": username,
            "password": password,
            "user_prefix": user_prefix,
            "app_version": app_version,
        }
        data.update(self._token_store.access_token_request)

        body = await self._post(
            _TOKEN_PATH,
            data=data,
        )

        self._token_store.token = Token(body)