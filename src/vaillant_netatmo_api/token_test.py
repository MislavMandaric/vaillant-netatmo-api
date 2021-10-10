from authlib.oauth2.rfc6749 import OAuth2Token
import pytest

from .token import deserialize_token, serialize_token


@pytest.mark.asyncio
class TestToken:
    async def test_serialize_token__json_object__returns_json_string(self):
        token = OAuth2Token.from_dict({
            "access_token": "12345",
            "refresh_token": "abcde",
            "expires_at": "",
            "expires_in": ""
        })

        expected_json = '{"access_token": "12345", "refresh_token": "abcde", "expires_at": "", "expires_in": ""}'

        json = serialize_token(token)

        assert json == expected_json

    async def test_deserialize_token__json_string__returns_json_oauth_object(self):
        json = '{"access_token": "12345", "refresh_token": "abcde", "expires_at": "", "expires_in": ""}'
        
        expected_token = OAuth2Token.from_dict({
            "access_token": "12345",
            "refresh_token": "abcde",
            "expires_at": "",
            "expires_in": ""
        })

        token = deserialize_token(json)

        assert isinstance(token, OAuth2Token)
        assert token == expected_token