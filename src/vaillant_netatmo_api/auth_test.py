import pytest

from authlib.oauth2.rfc6749.wrappers import OAuth2Token
import httpx

from .auth import auth_client
from .errors import RequestClientException

get_token_request = {
    "grant_type": "password",
    "username": "user",
    "password": "pass",
    "user_prefix": "prefix",
    "app_version": "version",
    "scope": "scope",
    "client_id": "client",
    "client_secret": "secret",
}

get_token_response = {
    "access_token": "12345",
    "refresh_token": "abcde",
    "expires_at": "",
    "expires_in": ""
}

@pytest.mark.asyncio
class TestAuth:
    async def test_async_get_token__invalid_request_params__raises_error(self, respx_mock):
        respx_mock.post("https://api.netatmo.com/oauth2/token", data=get_token_request).respond(400)

        async with auth_client(get_token_request["client_id"], get_token_request["client_secret"], get_token_request["scope"]) as client:
            with pytest.raises(RequestClientException):
                await client.async_get_token(get_token_request["username"], get_token_request["password"], get_token_request["user_prefix"], get_token_request["app_version"])

    async def test_async_get_token__server_errors__retry_until_success(self, respx_mock):
        respx_mock.post("https://api.netatmo.com/oauth2/token", data=get_token_request).mock(side_effect=[
            httpx.Response(500),
            httpx.Response(200, json=get_token_response),
        ])

        async with auth_client(get_token_request["client_id"], get_token_request["client_secret"], get_token_request["scope"]) as client:
            token = await client.async_get_token(get_token_request["username"], get_token_request["password"], get_token_request["user_prefix"], get_token_request["app_version"])

            assert respx_mock.calls.call_count == 2
            assert isinstance(token, OAuth2Token)
            assert token == get_token_response

    async def test_async_get_token__valid_request_params__returns_valid_oauth_token(self, respx_mock):
        respx_mock.post("https://api.netatmo.com/oauth2/token", data=get_token_request).respond(200, json=get_token_response)

        async with auth_client(get_token_request["client_id"], get_token_request["client_secret"], get_token_request["scope"]) as client:
            token = await client.async_get_token(get_token_request["username"], get_token_request["password"], get_token_request["user_prefix"], get_token_request["app_version"])

            assert isinstance(token, OAuth2Token)
            assert token == get_token_response