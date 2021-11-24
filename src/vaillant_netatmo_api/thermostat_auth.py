from __future__ import annotations

from typing import Generator
from urllib.parse import urlencode

from httpx import Auth, Headers, Request, Response, codes

from .token import Token, TokenStore

_TOKEN_PATH = "/oauth2/token"


class ThermostatAuth(Auth):
    """
    Thermostat client's Auth implementation of the httpx auth middleware.
    
    For each request appends access token to the request body and handles refreshing access token after it expires.
    """

    requires_request_body = True
    requires_response_body = True

    def __init__(self, token_store: TokenStore) -> None:
        """
        Create auth instance.

        Uses token store to get and update tokens.
        """

        self._token_store = token_store

    def auth_flow(self, request: Request) -> Generator[Request, Response, None]:
        """
        Implementation of the extension point in auth middleware.

        Adds access token to request. If it fails, refreshes token and tries again.
        """

        response = yield self._get_access_token_request(request)

        if response.status_code == codes.UNAUTHORIZED or response.status_code == codes.FORBIDDEN:
            refresh_response = yield self._get_refresh_token_request(request)
            self._process_refresh_response(refresh_response)

            yield self._get_access_token_request(request)

    def _get_access_token_request(self, request: Request) -> Request:
        method = request.method
        url = request.url
        content = self._content_with_access_token(request.content)
        headers = self._headers_without_content_length(request.headers)

        return Request(
            method,
            url,
            content=content,
            headers=headers,
        )

    def _get_refresh_token_request(self, request: Request) -> Request:
        method = "POST"
        url = request.url.join(_TOKEN_PATH)
        data = self._token_store.refresh_token_request

        return Request(
            method,
            url,
            data=data,
        )
    
    def _process_refresh_response(self, response: Response) -> None:
        if not response.is_error:
            self._token_store.token = Token(response.json())

    def _headers_without_content_length(self, headers: Headers) -> Headers:
        headers = headers.copy()
        headers.pop("content-length")
        return headers

    def _content_with_access_token(self, content: bytes) -> bytes:
        access_token_content = b""
        if self._token_store.token is not None:
            key = "access_token"
            value = self._token_store.token.access_token
            access_token_content = urlencode([(key, value)], doseq=True).encode("utf-8")

        return b'&'.join([content, access_token_content])