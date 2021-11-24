import pytest

from time import time

from vaillant_netatmo_api.token import Token


@pytest.mark.asyncio
class TestToken:
    async def test_serialize__json_token_object__returns_json_string(self):
        token = Token({
            "access_token": "12345",
            "refresh_token": "abcde",
            "expires_at": 12,
            "expires_in": ""
        })

        expected_json = '{"access_token": "12345", "refresh_token": "abcde", "expires_at": 12}'

        json = token.serialize()

        assert json == expected_json

    async def test_deserialize__json_string__returns_json_token_object(self):
        json = '{"access_token": "12345", "refresh_token": "abcde", "expires_at": 12}'
        
        expected_token = Token({
            "access_token": "12345",
            "refresh_token": "abcde",
            "expires_at": 12,
        })

        token = Token.deserialize(json)

        assert isinstance(token, Token)
        assert token == expected_token

    async def test_is_expired__invalid_token__returns_true(self):
        token = Token({
            "access_token": "12345",
            "refresh_token": "abcde",
            "expires_at": "invalid",
        })

        is_expired = token.is_expired

        assert is_expired == True

    async def test_is_expired__expired_token__returns_true(self):
        token = Token({
            "access_token": "12345",
            "refresh_token": "abcde",
            "expires_at": int(time()) - 1000,
        })

        is_expired = token.is_expired

        assert is_expired == True

    async def test_is_expired__non_expired_token__returns_false(self):
        token = Token({
            "access_token": "12345",
            "refresh_token": "abcde",
            "expires_at": int(time()) + 1000,
        })

        is_expired = token.is_expired

        assert is_expired == False