import httpx
import pytest

from respx import MockRouter

from vaillant_netatmo_api.errors import RequestClientException
from vaillant_netatmo_api.thermostat import thermostat_client
from vaillant_netatmo_api.token import Token
from vaillant_netatmo_api.home import Home

token = Token({
    "access_token": "12345",
    "refresh_token": "abcde",
    "expires_at": "",
})


get_homes_data_request = {
    "app_type": "app_thermostat_vaillant",
    "app_identifier": "app_thermostat_vaillant",
    "sync_measurements": True,
}

get_homes_data_refreshed_request = {
    "device_type": "NAVaillant",
    "data_amount": "app",
    "sync_device_id": "all",
}

get_homes_data_response = {
    "status": "ok",
    "body": {
        "homes": [
            {
                "id": "id",
                "name": "name",
                "roomes": [
                    {
                        "id": "id",
                    }
                ]
            }
        ]
    }
}

refresh_token_request = {
    "grant_type": "refresh_token",
    "client_id": "client",
    "client_secret": "secret",
    "refresh_token": "abcde",
}

refresh_token_response = {
    "access_token": "67890",
    "refresh_token": "fghij",
    "expires_at": "",
}


@pytest.mark.asyncio
class TestThermostatHome:
    async def test_async_get_homes_data__invalid_request_params__raises_error(self, respx_mock: MockRouter):
        respx_mock.post("https://app.netatmo.net/api/homesdata",
                        json=get_homes_data_request, headers={("authorization", "Bearer 12345")}).respond(400)

        async with thermostat_client("", "", token, None) as client:
            with pytest.raises(RequestClientException):
                await client.async_get_homes_data()

    @pytest.mark.skip(reason="second call gets marked as 'not mocked' even though all is ok when testing manually (hint: because of authorization header)")
    async def test_async_get_homes_data__server_errors__retry_until_success(self, respx_mock: MockRouter):
        respx_mock.post("https://app.netatmo.net/api/homesdata",
                        json=get_homes_data_request, headers={("authorization", "Bearer 12345")}).respond(401)
        respx_mock.post("https://app.netatmo.net/oauth2/token",
                        data=refresh_token_request).respond(200, json=refresh_token_response)
        respx_mock.post("https://app.netatmo.net/api/homesdata",
                        json=get_homes_data_refreshed_request, headers={("authorization", "Bearer 67890")}).respond(200, json=get_homes_data_response)

        async with thermostat_client(refresh_token_request["client_id"], refresh_token_request["client_secret"], token, None) as client:
            homes = await client.async_get_homes_data()

            expected_homes = get_homes_data_response["body"]["homes"]

            assert respx_mock.calls.call_count == 3
            assert len(homes) == len(expected_homes)
            for x in zip(homes, expected_homes):
                assert x[0] == Home(**x[1])

    async def test_async_get_homes_data__unauthorized_errors__succeed_after_refreshing_token(self, respx_mock: MockRouter):
        respx_mock.post("https://app.netatmo.net/api/homesdata", json=get_homes_data_request, headers={("authorization", "Bearer 12345")}).mock(side_effect=[
            httpx.Response(500),
            httpx.Response(200, json=get_homes_data_response),
        ])

        async with thermostat_client("", "", token, None) as client:
            homes = await client.async_get_homes_data()

            expected_homes = get_homes_data_response["body"]["homes"]

            assert respx_mock.calls.call_count == 2
            assert len(homes) == len(expected_homes)
            for x in zip(homes, expected_homes):
                assert x[0] == Home(**x[1])

    async def test_async_get_homes_data__valid_request_params__returns_valid_device_list(self, respx_mock: MockRouter):
        respx_mock.post("https://app.netatmo.net/api/homesdata",
                        json=get_homes_data_request, headers={("authorization", "Bearer 12345")}).respond(200, json=get_homes_data_response)

        async with thermostat_client("", "", token, None) as client:
            homes = await client.async_get_homes_data()

            expected_homes = get_homes_data_response["body"]["homes"]

            assert len(homes) == len(expected_homes)
            for x in zip(homes, expected_homes):
                assert x[0] == Home(**x[1])
