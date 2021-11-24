"""Module containing helper methods for JSON serialization and deserialization of bearer tokens."""

from __future__ import annotations

import json

from time import time
from typing import Callable


class TokenStore:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        token: Token | None = None,
        on_token_update: Callable[[Token], None] = None,
    ) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._token = token
        self._on_token_update = on_token_update

    @property
    def token(self) -> Token | None:
        return self._token

    @token.setter
    def token(self, value: Token) -> None:
        self._token = value

        if self._on_token_update is not None:
            self._on_token_update(self._token)
    
    @property
    def access_token_request(self) -> dict:
        return {
            "grant_type": "password",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "scope": "read_thermostat write_thermostat",
        }
    
    @property
    def refresh_token_request(self) -> dict:
        return {
            "grant_type": "refresh_token",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "refresh_token": self._token.refresh_token,
        }


class Token:
    def __init__(self, params: dict) -> None:
        access_token = params.get('access_token')
        refresh_token = params.get('refresh_token')
        expires_at = None

        if isinstance(params.get('expires_at'), int):
            expires_at = params.get('expires_at')
        elif isinstance(params.get('expires_in'), int):
            expires_at = int(time()) + params.get('expires_in')

        self._access_token = access_token
        self._refresh_token = refresh_token
        self._expires_at = expires_at

    def __eq__(self, other: Token):
        if (not isinstance(other, Token)):
            return False
        
        return self._access_token == other._access_token and \
            self._refresh_token == other._refresh_token and \
            self._expires_at == other._expires_at
    
    @property
    def access_token(self) -> str:
        return self._access_token
    
    @property
    def refresh_token(self) -> str:
        return self._refresh_token

    @property
    def is_expired(self) -> bool:
        if not self._expires_at:
            return True

        return self._expires_at < time()

    def serialize(self) -> str:
        """Serialize token object into a JSON string."""

        return json.dumps({
            "access_token": self._access_token,
            "refresh_token": self._refresh_token,
            "expires_at": self._expires_at,
        })

    @classmethod
    def deserialize(cls, token: str) -> Token:
        """Deserialize JSON string into a token object."""

        return Token(json.loads(token))
