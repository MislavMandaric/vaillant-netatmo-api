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
    "access_token": "12345",
}

get_thermostats_data_refreshed_request = {
    "device_type": "NAVaillant",
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
                "system_mode": "summer",
                "setpoint_default_duration": 120,
                "setpoint_hwb": {"setpoint_activate": False},
                "modules": [
                    {
                        "_id": "id",
                        "type": "type",
                        "module_name": "module_name",
                        "firmware": "firmware",
                        "battery_percent": 80,
                        "setpoint_away": {"setpoint_activate": False},
                        "setpoint_manual": {"setpoint_activate": False},
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

set_system_mode_request = {
    "device_id": "device",
    "module_id": "module",
    "system_mode": "summer",
    "access_token": "12345",
}

set_system_mode_response = {
    "status": "ok",
}

set_minor_mode_request = {
    "device_id": "device",
    "module_id": "module",
    "setpoint_mode": "away",
    "activate": True,
    "access_token": "12345",
}

set_minor_mode_response = {
    "status": "ok",
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
        respx_mock.post("https://api.netatmo.com/api/getthermostatsdata", data=get_thermostats_data_request).respond(400)

        async with thermostat_client("", "", token, None) as client:
            with pytest.raises(RequestClientException):
                await client.async_get_thermostats_data()

    async def test_async_get_thermostats_data__server_errors__retry_until_success(self, respx_mock: MockRouter):
        respx_mock.post("https://api.netatmo.com/api/getthermostatsdata", data=get_thermostats_data_request).respond(401)
        respx_mock.post("https://api.netatmo.com/oauth2/token", data=refresh_token_request).respond(200, json=refresh_token_response)
        respx_mock.post("https://api.netatmo.com/api/getthermostatsdata", data=get_thermostats_data_refreshed_request).respond(200, json=get_thermostats_data_response)

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
        respx_mock.post("https://api.netatmo.com/api/getthermostatsdata", data=get_thermostats_data_request).respond(200, json=get_thermostats_data_response)

        async with thermostat_client("", "", token, None) as client:
            devices = await client.async_get_thermostats_data()

            expected_devices = get_thermostats_data_response["body"]["devices"]

            assert len(devices) == len(expected_devices)
            for x in zip(devices, expected_devices):
                assert x[0] == Device(**x[1])

    async def test_async_get_thermostats_data__request_data__contains_ts_param(self, respx_mock: MockRouter, mocker: MockerFixture):
        some_time = datetime(2021, 11, 22, 1, 0)

        mocker.patch("vaillant_netatmo_api.base.now", return_value=some_time)

        respx_mock.post("https://api.netatmo.com/api/getthermostatsdata", data=get_thermostats_data_request).respond(200, json=get_thermostats_data_response)

        async with thermostat_client("", "", token, None) as client:
            _ = await client.async_get_thermostats_data()

            assert respx_mock.calls.last.request.url.params["ts"] == str(round(some_time.timestamp()))

    async def test_async_get_measure__invalid_request_params__raises_error(self, respx_mock: MockRouter):
        respx_mock.post("https://api.netatmo.com/api/getmeasure", data=get_measure_request).respond(400)

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
        respx_mock.post("https://api.netatmo.com/api/getmeasure", data=get_measure_request).respond(200, json=get_measure_response)

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

    async def test_async_set_system_mode__invalid_request_params__raises_error(self, respx_mock: MockRouter):
        respx_mock.post("https://api.netatmo.com/api/setsystemmode", data=set_system_mode_request).respond(400)

        async with thermostat_client("", "", token, None) as client:
            with pytest.raises(RequestClientException):
                await client.async_set_system_mode(set_system_mode_request["device_id"], set_system_mode_request["module_id"], SystemMode.SUMMER)

    async def test_async_set_system_mode__server_errors__retry_until_success(self, respx_mock: MockRouter):
        respx_mock.post("https://api.netatmo.com/api/setsystemmode", data=set_system_mode_request).mock(side_effect=[
            httpx.Response(500),
            httpx.Response(200, json=set_system_mode_response),
        ])

        async with thermostat_client("", "", token, None) as client:
            await client.async_set_system_mode(set_system_mode_request["device_id"], set_system_mode_request["module_id"], SystemMode.SUMMER)

            assert respx_mock.calls.call_count == 2

    async def test_async_set_system_mode__valid_request_params__doesnt_raise_error(self, respx_mock: MockRouter):
        respx_mock.post("https://api.netatmo.com/api/setsystemmode", data=set_system_mode_request).respond(200, json=set_system_mode_response)

        async with thermostat_client("", "", token, None) as client:
            await client.async_set_system_mode(set_system_mode_request["device_id"], set_system_mode_request["module_id"], SystemMode.SUMMER)

    async def test_async_set_minor_mode__invalid_request_params__raises_error(self, respx_mock: MockRouter):
        respx_mock.post("https://api.netatmo.com/api/setminormode", data=set_minor_mode_request).respond(400)

        async with thermostat_client("", "", token, None) as client:
            with pytest.raises(RequestClientException):
                await client.async_set_minor_mode(set_minor_mode_request["device_id"], set_minor_mode_request["module_id"], SetpointMode.AWAY, True)

    async def test_async_set_minor_mode__server_errors__retry_until_success(self, respx_mock: MockRouter):
        respx_mock.post("https://api.netatmo.com/api/setminormode", data=set_minor_mode_request).mock(side_effect=[
            httpx.Response(500),
            httpx.Response(200, json=set_minor_mode_response),
        ])

        async with thermostat_client("", "", token, None) as client:
            await client.async_set_minor_mode(
                set_minor_mode_request["device_id"],
                set_minor_mode_request["module_id"],
                SetpointMode.AWAY,
                True,
            )

            assert respx_mock.calls.call_count == 2

    async def test_async_set_minor_mode__activate_manual_without_temp_and_endtime__raises_error(self):
        async with thermostat_client("", "", token, None) as client:
            with pytest.raises(UnsuportedArgumentsException):
                await client.async_set_minor_mode(
                    "device",
                    "module",
                    SetpointMode.MANUAL,
                    True,
                )
    
    async def test_async_set_minor_mode__activate_manual_without_temp__raises_error(self):
        async with thermostat_client("", "", token, None) as client:
            with pytest.raises(UnsuportedArgumentsException):
                await client.async_set_minor_mode(
                    "device",
                    "module",
                    SetpointMode.MANUAL,
                    True,
                    setpoint_endtime=datetime.now(),
                )
    
    async def test_async_set_minor_mode__activate_manual_without_endtime__raises_error(self):
        async with thermostat_client("", "", token, None) as client:
            with pytest.raises(UnsuportedArgumentsException):
                await client.async_set_minor_mode(
                    "device",
                    "module",
                    SetpointMode.MANUAL,
                    True,
                    setpoint_temp=25,
                )

    async def test_async_set_minor_mode__activate_manual_with_temp_and_endtime__executes_successfully(self, respx_mock: MockRouter, mocker: MockerFixture):
        some_time = datetime(2021, 11, 22, 1, 0)

        mocker.patch("vaillant_netatmo_api.thermostat.now", return_value=some_time)

        endtime = some_time + timedelta(seconds=10)

        set_minor_mode_request = {
            "device_id": "device",
            "module_id": "module",
            "setpoint_mode": "manual",
            "activate": True,
            "setpoint_endtime": int(endtime.timestamp()),
            "setpoint_temp": 25,
            "access_token": "12345",
        }

        set_minor_mode_response = {
            "status": "ok",
        }
        
        respx_mock.post("https://api.netatmo.com/api/setminormode", data=set_minor_mode_request).respond(200, json=set_minor_mode_response)

        async with thermostat_client("", "", token, None) as client:
            await client.async_set_minor_mode(
                set_minor_mode_request["device_id"],
                set_minor_mode_request["module_id"],
                SetpointMode.MANUAL,
                True,
                setpoint_endtime=endtime,
                setpoint_temp=25,
            )

    async def test_async_set_minor_mode__deactivate_manual_with_temp_and_endtime__raises_error(self):
        async with thermostat_client("", "", token, None) as client:
            with pytest.raises(UnsuportedArgumentsException):
                await client.async_set_minor_mode(
                    "device",
                    "module",
                    SetpointMode.MANUAL,
                    False,
                    setpoint_temp=25,
                    setpoint_endtime=datetime.now(),
                )

    async def test_async_set_minor_mode__deactivate_manual_with_temp__raises_error(self):
        async with thermostat_client("", "", token, None) as client:
            with pytest.raises(UnsuportedArgumentsException):
                await client.async_set_minor_mode(
                    "device",
                    "module",
                    SetpointMode.MANUAL,
                    False,
                    setpoint_temp=25,
                )
    
    async def test_async_set_minor_mode__deactivate_manual_with_endtime__raises_error(self):
        async with thermostat_client("", "", token, None) as client:
            with pytest.raises(UnsuportedArgumentsException):
                await client.async_set_minor_mode(
                    "device",
                    "module",
                    SetpointMode.MANUAL,
                    False,
                    setpoint_endtime=datetime.now(),
                )

    async def test_async_set_minor_mode__deactivate_manual_without_temp_and_endtime__executes_successfully(self, respx_mock: MockRouter):
        set_minor_mode_request = {
            "device_id": "device",
            "module_id": "module",
            "setpoint_mode": "manual",
            "activate": False,
            "access_token": "12345",
        }

        set_minor_mode_response = {
            "status": "ok",
        }
        
        respx_mock.post("https://api.netatmo.com/api/setminormode", data=set_minor_mode_request).respond(200, json=set_minor_mode_response)

        async with thermostat_client("", "", token, None) as client:
            await client.async_set_minor_mode(
                set_minor_mode_request["device_id"],
                set_minor_mode_request["module_id"],
                SetpointMode.MANUAL,
                False,
            )

    async def test_async_set_minor_mode__activate_away_without_temp_and_endtime__executes_successfully(self, respx_mock: MockRouter):
        set_minor_mode_request = {
            "device_id": "device",
            "module_id": "module",
            "setpoint_mode": "away",
            "activate": True,
            "access_token": "12345",
        }

        set_minor_mode_response = {
            "status": "ok",
        }
        
        respx_mock.post("https://api.netatmo.com/api/setminormode", data=set_minor_mode_request).respond(200, json=set_minor_mode_response)

        async with thermostat_client("", "", token, None) as client:
            await client.async_set_minor_mode(
                set_minor_mode_request["device_id"],
                set_minor_mode_request["module_id"],
                SetpointMode.AWAY,
                True,
            )

    async def test_async_set_minor_mode__activate_away_without_temp__executes_successfully(self, respx_mock: MockRouter, mocker: MockerFixture):
        some_time = datetime(2021, 11, 22, 1, 0)

        mocker.patch("vaillant_netatmo_api.thermostat.now", return_value=some_time)

        endtime = some_time + timedelta(seconds=10)
        
        set_minor_mode_request = {
            "device_id": "device",
            "module_id": "module",
            "setpoint_mode": "away",
            "activate": True,
            "setpoint_endtime": int(endtime.timestamp()),
            "access_token": "12345",
        }

        set_minor_mode_response = {
            "status": "ok",
        }
        
        respx_mock.post("https://api.netatmo.com/api/setminormode", data=set_minor_mode_request).respond(200, json=set_minor_mode_response)

        async with thermostat_client("", "", token, None) as client:
            await client.async_set_minor_mode(
                set_minor_mode_request["device_id"],
                set_minor_mode_request["module_id"],
                SetpointMode.AWAY,
                True,
                setpoint_endtime=endtime,
            )
    
    async def test_async_set_minor_mode__activate_away_without_endtime__raises_error(self):
        async with thermostat_client("", "", token, None) as client:
            with pytest.raises(UnsuportedArgumentsException):
                await client.async_set_minor_mode(
                    "device",
                    "module",
                    SetpointMode.AWAY,
                    True,
                    setpoint_temp=25,
                )
    
    async def test_async_set_minor_mode__activate_away_with_temp_and_endtime__raises_error(self):
        async with thermostat_client("", "", token, None) as client:
            with pytest.raises(UnsuportedArgumentsException):
                await client.async_set_minor_mode(
                    "device",
                    "module",
                    SetpointMode.AWAY,
                    True,
                    setpoint_temp=25,
                    setpoint_endtime=datetime.now(),
                )

    async def test_async_set_minor_mode__deactivate_away_with_temp_and_endtime__raises_error(self):
        async with thermostat_client("", "", token, None) as client:
            with pytest.raises(UnsuportedArgumentsException):
                await client.async_set_minor_mode(
                    "device",
                    "module",
                    SetpointMode.AWAY,
                    False,
                    setpoint_temp=25,
                    setpoint_endtime=datetime.now(),
                )

    async def test_async_set_minor_mode__deactivate_away_with_temp__raises_error(self):
        async with thermostat_client("", "", token, None) as client:
            with pytest.raises(UnsuportedArgumentsException):
                await client.async_set_minor_mode(
                    "device",
                    "module",
                    SetpointMode.AWAY,
                    False,
                    setpoint_temp=25,
                )
    
    async def test_async_set_minor_mode__deactivate_away_with_endtime__raises_error(self):
        async with thermostat_client("", "", token, None) as client:
            with pytest.raises(UnsuportedArgumentsException):
                await client.async_set_minor_mode(
                    "device",
                    "module",
                    SetpointMode.AWAY,
                    False,
                    setpoint_endtime=datetime.now(),
                )

    async def test_async_set_minor_mode__deactivate_away_without_temp_and_endtime__executes_successfully(self, respx_mock: MockRouter):
        set_minor_mode_request = {
            "device_id": "device",
            "module_id": "module",
            "setpoint_mode": "away",
            "activate": False,
            "access_token": "12345",
        }

        set_minor_mode_response = {
            "status": "ok",
        }
        
        respx_mock.post("https://api.netatmo.com/api/setminormode", data=set_minor_mode_request).respond(200, json=set_minor_mode_response)

        async with thermostat_client("", "", token, None) as client:
            await client.async_set_minor_mode(
                set_minor_mode_request["device_id"],
                set_minor_mode_request["module_id"],
                SetpointMode.AWAY,
                False,
            )

    async def test_async_set_minor_mode__activate_hwb_without_temp_and_endtime__raises_error(self):
        async with thermostat_client("", "", token, None) as client:
            with pytest.raises(UnsuportedArgumentsException):
                await client.async_set_minor_mode(
                    "device",
                    "module",
                    SetpointMode.HWB,
                    True,
                )

    async def test_async_set_minor_mode__activate_hwb_without_temp__executes_successfully(self, respx_mock: MockRouter, mocker: MockerFixture):
        some_time = datetime(2021, 11, 22, 1, 0)

        mocker.patch("vaillant_netatmo_api.thermostat.now", return_value=some_time)

        endtime = some_time + timedelta(seconds=10)

        set_minor_mode_request = {
            "device_id": "device",
            "module_id": "module",
            "setpoint_mode": "away",
            "activate": True,
            "setpoint_endtime": int(endtime.timestamp()),
            "access_token": "12345",
        }

        set_minor_mode_response = {
            "status": "ok",
        }
        
        respx_mock.post("https://api.netatmo.com/api/setminormode", data=set_minor_mode_request).respond(200, json=set_minor_mode_response)

        async with thermostat_client("", "", token, None) as client:
            await client.async_set_minor_mode(
                set_minor_mode_request["device_id"],
                set_minor_mode_request["module_id"],
                SetpointMode.AWAY,
                True,
                setpoint_endtime=endtime,
            )
    
    async def test_async_set_minor_mode__activate_hwb_without_endtime__raises_error(self):
        async with thermostat_client("", "", token, None) as client:
            with pytest.raises(UnsuportedArgumentsException):
                await client.async_set_minor_mode(
                    "device",
                    "module",
                    SetpointMode.HWB,
                    True,
                    setpoint_temp=25,
                )
    
    async def test_async_set_minor_mode__activate_hwb_with_temp_and_endtime__raises_error(self):
        async with thermostat_client("", "", token, None) as client:
            with pytest.raises(UnsuportedArgumentsException):
                await client.async_set_minor_mode(
                    "device",
                    "module",
                    SetpointMode.HWB,
                    True,
                    setpoint_temp=25,
                    setpoint_endtime=datetime.now(),
                )

    async def test_async_set_minor_mode__deactivate_hwb_with_temp_and_endtime__raises_error(self):
        async with thermostat_client("", "", token, None) as client:
            with pytest.raises(UnsuportedArgumentsException):
                await client.async_set_minor_mode(
                    "device",
                    "module",
                    SetpointMode.HWB,
                    False,
                    setpoint_temp=25,
                    setpoint_endtime=datetime.now(),
                )

    async def test_async_set_minor_mode__deactivate_hwb_with_temp__raises_error(self):
        async with thermostat_client("", "", token, None) as client:
            with pytest.raises(UnsuportedArgumentsException):
                await client.async_set_minor_mode(
                    "device",
                    "module",
                    SetpointMode.HWB,
                    False,
                    setpoint_temp=25,
                )
    
    async def test_async_set_minor_mode__deactivate_hwb_with_endtime__raises_error(self):
        async with thermostat_client("", "", token, None) as client:
            with pytest.raises(UnsuportedArgumentsException):
                await client.async_set_minor_mode(
                    "device",
                    "module",
                    SetpointMode.HWB,
                    False,
                    setpoint_endtime=datetime.now(),
                )

    async def test_async_set_minor_mode__deactivate_hwb_without_temp_and_endtime__executes_successfully(self, respx_mock: MockRouter):
        set_minor_mode_request = {
            "device_id": "device",
            "module_id": "module",
            "setpoint_mode": "hwb",
            "activate": False,
            "access_token": "12345",
        }

        set_minor_mode_response = {
            "status": "ok",
        }
        
        respx_mock.post("https://api.netatmo.com/api/setminormode", data=set_minor_mode_request).respond(200, json=set_minor_mode_response)

        async with thermostat_client("", "", token, None) as client:
            await client.async_set_minor_mode(
                set_minor_mode_request["device_id"],
                set_minor_mode_request["module_id"],
                SetpointMode.HWB,
                False,
            )

    async def test_async_sync_schedule__invalid_request_params__raises_error(self, respx_mock: MockRouter):
        respx_mock.post("https://api.netatmo.com/api/syncschedule", data=sync_schedule_request).respond(400)

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
        respx_mock.post("https://api.netatmo.com/api/syncschedule", data=sync_schedule_request).respond(200, json=sync_schedule_response)

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
        respx_mock.post("https://api.netatmo.com/api/switchschedule", data=switch_schedule_request).respond(400)

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
        respx_mock.post("https://api.netatmo.com/api/switchschedule", data=switch_schedule_request).respond(200, json=switch_schedule_response)

        async with thermostat_client("", "", token, None) as client:
            await client.async_switch_schedule(
                sync_schedule_request["device_id"],
                sync_schedule_request["module_id"],
                sync_schedule_request["schedule_id"],
            )
