import httpx
import pytest

from datetime import datetime, timedelta

from pytest_mock import MockerFixture
from respx import MockRouter

from vaillant_netatmo_api.errors import RequestClientException, UnsuportedArgumentsException
from vaillant_netatmo_api.thermostat import Device, MeasurementItem, MeasurementScale, MeasurementType, SetpointMode, SystemMode, TimeSlot, Zone, thermostat_client
from vaillant_netatmo_api.token import Token

token = Token({
    "access_token": "12345",
    "refresh_token": "abcde",
    "expires_at": "",
})

get_thermostats_data_request = {
    "device_type": "NAVaillant",
    "data_amount": "app",
    "sync_device_id": "all",
    "access_token": "12345",
}

get_thermostats_data_refreshed_request = {
    "device_type": "NAVaillant",
    "data_amount": "app",
    "sync_device_id": "all",
    "access_token": "67890",
}

get_thermostats_data_response = {
    "status": "ok",
    "body": {
        "devices": [
            {
                "_id": "id",
                "type": "type",
                "station_name": "station_name",
                "firmware": "firmware",
                "wifi_status": 60,
                "dhw": 55,
                "dhw_max": 65,
                "dhw_min": 35,
                "setpoint_default_duration": 120,
                "outdoor_temperature": {
                    "te": 11,
                    "ti": 1667636447,
                },
                "system_mode": "summer",
                "setpoint_hwb": {"setpoint_activate": False, "setpoint_endtime": 1642056298},
                "modules": [
                    {
                        "_id": "id",
                        "type": "type",
                        "module_name": "module_name",
                        "firmware": "firmware",
                        "rf_status": 70,
                        "boiler_status": True,
                        "battery_percent": 80,
                        "setpoint_away": {"setpoint_activate": False, "setpoint_endtime": 1642056298},
                        "setpoint_manual": {"setpoint_activate": False, "setpoint_endtime": 1642056298},
                        "therm_program_list": [
                            {
                                "zones": [{"temp": 20, "id": 0, "hw": True}],
                                "timetable": [{"id": 0, "m_offset": 0}],
                                "program_id": "program_id",
                                "name": "name",
                                "selected": True,
                            }
                        ],
                        "measured": {"temperature": 25, "setpoint_temp": 26, "est_setpoint_temp": 27},
                    }
                ]
            }
        ]
    }
}

get_measure_request = {
    "device_id": "device",
    "module_id": "module",
    "type": "temperature",
    "scale": "max",
    "date_begin": 1642252768,
    "access_token": "12345",
}

get_measure_response = {
    "status": "ok",
    "body": [
        {"beg_time": 1642252768, "step_time": 600, "value": [[20], [20.1]]},
        {"beg_time": 1642252768, "step_time": 600, "value": [[20.2], [20.3]]}
    ]
}

sync_schedule_request = {
    "device_id": "device",
    "module_id": "module",
    "schedule_id": "program_id",
    "name": "name",
    "zones": "[{\"id\": 0, \"temp\": 20, \"hw\": true}]",
    "timetable": "[{\"id\": 0, \"m_offset\": 0}]",
    "access_token": "12345",
}

sync_schedule_response = {
    "status": "ok",
}

switch_schedule_request = {
    "device_id": "device",
    "module_id": "module",
    "schedule_id": "program_id",
    "access_token": "12345",
}

switch_schedule_response = {
    "status": "ok",
}

async_set_hot_water_temperature_request = {
    "device_id": "device",
    "dhw": 50,
    "access_token": "12345",
}

async_set_hot_water_temperature_response = {
    "status": "ok",
}

async_modify_device_param_request = {
    "device_id": "device",
    "setpoint_default_duration": 120,
    "access_token": "12345",
}

async_modify_device_param_response = {
    "status": "ok",
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
class TestThermostat:
    async def test_async_get_thermostats_data__invalid_request_params__raises_error(self, respx_mock: MockRouter):
        respx_mock.post("https://api.netatmo.com/api/getthermostatsdata",
                        data=get_thermostats_data_request).respond(400)

        async with thermostat_client("", "", token, None) as client:
            with pytest.raises(RequestClientException):
                await client.async_get_thermostats_data()

    async def test_async_get_thermostats_data__server_errors__retry_until_success(self, respx_mock: MockRouter):
        respx_mock.post("https://api.netatmo.com/api/getthermostatsdata",
                        data=get_thermostats_data_request).respond(401)
        respx_mock.post("https://api.netatmo.com/oauth2/token",
                        data=refresh_token_request).respond(200, json=refresh_token_response)
        respx_mock.post("https://api.netatmo.com/api/getthermostatsdata",
                        data=get_thermostats_data_refreshed_request).respond(200, json=get_thermostats_data_response)

        async with thermostat_client(refresh_token_request["client_id"], refresh_token_request["client_secret"], token, None) as client:
            devices = await client.async_get_thermostats_data()

            expected_devices = get_thermostats_data_response["body"]["devices"]

            assert respx_mock.calls.call_count == 3
            assert len(devices) == len(expected_devices)
            for x in zip(devices, expected_devices):
                assert x[0] == Device(**x[1])

    async def test_async_get_thermostats_data__unauthorized_errors__succeed_after_refreshing_token(self, respx_mock: MockRouter):
        respx_mock.post("https://api.netatmo.com/api/getthermostatsdata", data=get_thermostats_data_request).mock(side_effect=[
            httpx.Response(500),
            httpx.Response(200, json=get_thermostats_data_response),
        ])

        async with thermostat_client("", "", token, None) as client:
            devices = await client.async_get_thermostats_data()

            expected_devices = get_thermostats_data_response["body"]["devices"]

            assert respx_mock.calls.call_count == 2
            assert len(devices) == len(expected_devices)
            for x in zip(devices, expected_devices):
                assert x[0] == Device(**x[1])

    async def test_async_get_thermostats_data__valid_request_params__returns_valid_device_list(self, respx_mock: MockRouter):
        respx_mock.post("https://api.netatmo.com/api/getthermostatsdata",
                        data=get_thermostats_data_request).respond(200, json=get_thermostats_data_response)

        async with thermostat_client("", "", token, None) as client:
            devices = await client.async_get_thermostats_data()

            expected_devices = get_thermostats_data_response["body"]["devices"]

            assert len(devices) == len(expected_devices)
            for x in zip(devices, expected_devices):
                assert x[0] == Device(**x[1])

    async def test_async_get_measure__invalid_request_params__raises_error(self, respx_mock: MockRouter):
        respx_mock.post("https://api.netatmo.com/api/getmeasure",
                        data=get_measure_request).respond(400)

        async with thermostat_client("", "", token, None) as client:
            with pytest.raises(RequestClientException):
                await client.async_get_measure(
                    get_measure_request["device_id"],
                    get_measure_request["module_id"],
                    MeasurementType.TEMPERATURE,
                    MeasurementScale.MAX,
                    datetime.fromtimestamp(get_measure_request["date_begin"]),
                )

    async def test_async_get_measure__valid_request_params__returns_valid_measurement_item_list(self, respx_mock: MockRouter):
        respx_mock.post("https://api.netatmo.com/api/getmeasure",
                        data=get_measure_request).respond(200, json=get_measure_response)

        async with thermostat_client("", "", token, None) as client:
            measurement_items = await client.async_get_measure(
                get_measure_request["device_id"],
                get_measure_request["module_id"],
                MeasurementType.TEMPERATURE,
                MeasurementScale.MAX,
                datetime.fromtimestamp(get_measure_request["date_begin"]),
            )

            expected_measurement_items = get_measure_response["body"]

            assert len(measurement_items) == len(expected_measurement_items)
            for x in zip(measurement_items, expected_measurement_items):
                assert x[0] == MeasurementItem(**x[1])

    async def test_async_sync_schedule__invalid_request_params__raises_error(self, respx_mock: MockRouter):
        respx_mock.post("https://api.netatmo.com/api/syncschedule",
                        data=sync_schedule_request).respond(400)

        async with thermostat_client("", "", token, None) as client:
            with pytest.raises(RequestClientException):
                await client.async_sync_schedule(
                    sync_schedule_request["device_id"],
                    sync_schedule_request["module_id"],
                    sync_schedule_request["schedule_id"],
                    sync_schedule_request["name"],
                    [Zone(**{"temp": 20, "id": 0, "hw": True})],
                    [TimeSlot(**{"id": 0, "m_offset": 0})],
                )

    async def test_async_sync_schedule__server_errors__retry_until_success(self, respx_mock: MockRouter):
        respx_mock.post("https://api.netatmo.com/api/syncschedule", data=sync_schedule_request).mock(side_effect=[
            httpx.Response(500),
            httpx.Response(200, json=sync_schedule_response),
        ])

        async with thermostat_client("", "", token, None) as client:
            await client.async_sync_schedule(
                sync_schedule_request["device_id"],
                sync_schedule_request["module_id"],
                sync_schedule_request["schedule_id"],
                sync_schedule_request["name"],
                [Zone(**{"temp": 20, "id": 0, "hw": True})],
                [TimeSlot(**{"id": 0, "m_offset": 0})],
            )

            assert respx_mock.calls.call_count == 2

    async def test_async_sync_schedule__valid_request_params__doesnt_raise_error(self, respx_mock: MockRouter):
        respx_mock.post("https://api.netatmo.com/api/syncschedule",
                        data=sync_schedule_request).respond(200, json=sync_schedule_response)

        async with thermostat_client("", "", token, None) as client:
            await client.async_sync_schedule(
                sync_schedule_request["device_id"],
                sync_schedule_request["module_id"],
                sync_schedule_request["schedule_id"],
                sync_schedule_request["name"],
                [Zone(**{"temp": 20, "id": 0, "hw": True})],
                [TimeSlot(**{"id": 0, "m_offset": 0})],
            )

    async def test_async_switch_schedule__invalid_request_params__raises_error(self, respx_mock: MockRouter):
        respx_mock.post("https://api.netatmo.com/api/switchschedule",
                        data=switch_schedule_request).respond(400)

        async with thermostat_client("", "", token, None) as client:
            with pytest.raises(RequestClientException):
                await client.async_switch_schedule(
                    sync_schedule_request["device_id"],
                    sync_schedule_request["module_id"],
                    sync_schedule_request["schedule_id"],
                )

    async def test_async_switch_schedule__server_errors__retry_until_success(self, respx_mock: MockRouter):
        respx_mock.post("https://api.netatmo.com/api/switchschedule", data=switch_schedule_request).mock(side_effect=[
            httpx.Response(500),
            httpx.Response(200, json=switch_schedule_response),
        ])

        async with thermostat_client("", "", token, None) as client:
            await client.async_switch_schedule(
                sync_schedule_request["device_id"],
                sync_schedule_request["module_id"],
                sync_schedule_request["schedule_id"],
            )

            assert respx_mock.calls.call_count == 2

    async def test_async_switch_schedule__valid_request_params__doesnt_raise_error(self, respx_mock: MockRouter):
        respx_mock.post("https://api.netatmo.com/api/switchschedule",
                        data=switch_schedule_request).respond(200, json=switch_schedule_response)

        async with thermostat_client("", "", token, None) as client:
            await client.async_switch_schedule(
                sync_schedule_request["device_id"],
                sync_schedule_request["module_id"],
                sync_schedule_request["schedule_id"],
            )

    async def test_async_set_hot_water_temperature__invalid_request_params__raises_error(self, respx_mock: MockRouter):
        respx_mock.post("https://api.netatmo.com/api/sethotwatertemperature",
                        data=async_set_hot_water_temperature_request).respond(400)

        async with thermostat_client("", "", token, None) as client:
            with pytest.raises(RequestClientException):
                await client.async_set_hot_water_temperature(
                    async_set_hot_water_temperature_request["device_id"],
                    async_set_hot_water_temperature_request["dhw"],
                )

    async def test_async_set_hot_water_temperature__server_errors__retry_until_success(self, respx_mock: MockRouter):
        respx_mock.post("https://api.netatmo.com/api/sethotwatertemperature", data=async_set_hot_water_temperature_request).mock(side_effect=[
            httpx.Response(500),
            httpx.Response(200, json=async_set_hot_water_temperature_response),
        ])

        async with thermostat_client("", "", token, None) as client:
            await client.async_set_hot_water_temperature(
                async_set_hot_water_temperature_request["device_id"],
                async_set_hot_water_temperature_request["dhw"],
            )

            assert respx_mock.calls.call_count == 2

    async def test_async_set_hot_water_temperature__valid_request_params__doesnt_raise_error(self, respx_mock: MockRouter):
        respx_mock.post("https://api.netatmo.com/api/sethotwatertemperature",
                        data=async_set_hot_water_temperature_request).respond(200, json=async_set_hot_water_temperature_response)

        async with thermostat_client("", "", token, None) as client:
            await client.async_set_hot_water_temperature(
                async_set_hot_water_temperature_request["device_id"],
                async_set_hot_water_temperature_request["dhw"],
            )

    async def test_async_modify_device_param__invalid_request_params__raises_error(self, respx_mock: MockRouter):
        respx_mock.post("https://api.netatmo.com/api/modifydeviceparam",
                        data=async_modify_device_param_request).respond(400)

        async with thermostat_client("", "", token, None) as client:
            with pytest.raises(RequestClientException):
                await client.async_modify_device_params(
                    async_modify_device_param_request["device_id"],
                    async_modify_device_param_request["setpoint_default_duration"],
                )

    async def test_async_modify_device_param__server_errors__retry_until_success(self, respx_mock: MockRouter):
        respx_mock.post("https://api.netatmo.com/api/modifydeviceparam", data=async_modify_device_param_request).mock(side_effect=[
            httpx.Response(500),
            httpx.Response(200, json=async_modify_device_param_response),
        ])

        async with thermostat_client("", "", token, None) as client:
            await client.async_modify_device_params(
                async_modify_device_param_request["device_id"],
                async_modify_device_param_request["setpoint_default_duration"],
            )

            assert respx_mock.calls.call_count == 2

    async def test_async_modify_device_param__valid_request_params__doesnt_raise_error(self, respx_mock: MockRouter):
        respx_mock.post("https://api.netatmo.com/api/modifydeviceparam",
                        data=async_modify_device_param_request).respond(200, json=async_modify_device_param_response)

        async with thermostat_client("", "", token, None) as client:
            await client.async_modify_device_params(
                async_modify_device_param_request["device_id"],
                async_modify_device_param_request["setpoint_default_duration"],
            )
