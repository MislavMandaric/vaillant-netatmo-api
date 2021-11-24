import httpx
import pytest

from pytest_mock import MockerFixture
from respx import MockRouter

from vaillant_netatmo_api.auth import auth_client
from vaillant_netatmo_api.errors import RequestClientException
from vaillant_netatmo_api.token import Token

get_token_request = {
    "username": "user",
    "password": "pass",
    "user_prefix": "prefix",
    "app_version": "version",
    "grant_type": "password",
    "client_id": "client",
    "client_secret": "secret",
    "scope": "read_thermostat write_thermostat",
}

get_token_response = {
    "access_token": "12345",
    "refresh_token": "abcde",
    "expires_at": "",
}

@pytest.mark.asyncio
class TestAuth:
    async def test_async_get_token__invalid_request_params__raises_error(self, respx_mock: MockRouter):
        respx_mock.post("https://api.netatmo.com/oauth2/token", data=get_token_request).respond(400)

        async with auth_client(get_token_request["client_id"], get_token_request["client_secret"], None) as client:
            with pytest.raises(RequestClientException):
                await client.async_token(get_token_request["username"], get_token_request["password"], get_token_request["user_prefix"], get_token_request["app_version"])

    async def test_async_get_token__server_errors__retry_until_success(self, respx_mock: MockRouter, mocker: MockerFixture):
        respx_mock.post("https://api.netatmo.com/oauth2/token", data=get_token_request).mock(side_effect=[
            httpx.Response(500),
            httpx.Response(200, json=get_token_response),
        ])

        on_token_update_stub = mocker.stub()

        async with auth_client(get_token_request["client_id"], get_token_request["client_secret"], on_token_update_stub) as client:
            await client.async_token(get_token_request["username"], get_token_request["password"], get_token_request["user_prefix"], get_token_request["app_version"])

            assert respx_mock.calls.call_count == 2
            on_token_update_stub.assert_called_once_with(Token(get_token_response))

    async def test_async_get_token__valid_request_params__returns_valid_oauth_token(self, respx_mock: MockRouter, mocker: MockerFixture):
        respx_mock.post("https://api.netatmo.com/oauth2/token", data=get_token_request).respond(200, json=get_token_response)

        on_token_update_stub = mocker.stub()

        async with auth_client(get_token_request["client_id"], get_token_request["client_secret"], on_token_update_stub) as client:
            await client.async_token(get_token_request["username"], get_token_request["password"], get_token_request["user_prefix"], get_token_request["app_version"])

            assert respx_mock.calls.call_count == 1
            on_token_update_stub.assert_called_once_with(Token(get_token_response))