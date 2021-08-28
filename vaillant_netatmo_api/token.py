"""Module containing helper methods for JSON serialization and deserialization of bearer tokens."""

from __future__ import annotations

import json

from authlib.oauth2.rfc6749 import OAuth2Token


def serialize_token(token: OAuth2Token) -> str:
    """Serialize token object into a JSON string."""

    return json.dumps(token)


def deserialize_token(token: str) -> OAuth2Token:
    """Deserialize JSON string into a token object."""

    return OAuth2Token.from_dict(json.loads(token))
