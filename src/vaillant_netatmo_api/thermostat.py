"""Module containing a ThermostatClient for the Netatmo API."""

from __future__ import annotations

import json

from contextlib import asynccontextmanager
from datetime import datetime, time
from enum import Enum
from typing import AsyncGenerator, Callable

from httpx import AsyncClient

from .home import HomeData, HomeStatus, ThermMode, TemperatureControlMode, ThermSetpointMode, Measure, MeasurementScale, MeasurementType, HomeMeasure, ScheduleType, HomeConfig
from .base import BaseClient
from .errors import NonOkResponseException, UnsuportedArgumentsException
from .thermostat_auth import ThermostatAuth
from .time import now
from .token import Token, TokenStore

_HOMES_DATA_PATH = "api/homesdata"
_GET_HOME_MEASURE_PATH = "api/gethomemeasure"
_HOME_STATUS_PATH = "syncapi/v1/homestatus"
_GET_CONFIGS_PATH = "syncapi/v1/getconfigs"
_SET_HOME_DATA_PATH = "api/sethomedata"
_SWITCH_HOME_SCHEDULE_PATH = "api/switchhomeschedule"
_SET_STATE_PATH = "syncapi/v1/setstate"
_SET_CONFIGS_PATH = "syncapi/v1/setconfigs"

_VAILLANT_APP_ID = "app_thermostat_vaillant"
_DEVICE_TYPE = "NAVaillant"
_RESPONSE_STATUS_OK = "ok"


@asynccontextmanager
async def thermostat_client(
    client_id: str,
    client_secret: str,
    token: Token,
    on_token_update: Callable[[Token], None],
) -> AsyncGenerator[ThermostatClient, None]:
    client = AsyncClient()
    token_store = TokenStore(client_id, client_secret, token, on_token_update)

    c = ThermostatClient(client, token_store)

    try:
        yield c
    finally:
        await client.aclose()


class ThermostatClient(BaseClient):
    """
    Client for making HTTP requests to the Netatmo API. Used for the subset of the API related to thermostats: getting thermostat data and changing thermostat modes.

    Uses BaseClient as a basis for making HTTP requests.
    """

    def __init__(
        self,
        client: AsyncClient,
        token_store: TokenStore,
    ) -> None:
        """
        Create new thermostat client instance.

        Uses the provided parameters to instantiate the BaseClient class.
        """

        super().__init__(client, ThermostatAuth(token_store))

    async def async_homes_data(self) -> list[HomeData]:
        """
        Get homes data from the Netatmo API.

        On success, returns a list of homes with their device data. On error, throws an exception.
        """
        path = _HOMES_DATA_PATH
        data = {
            "app_identifier": _VAILLANT_APP_ID,
            "app_type": _VAILLANT_APP_ID,
            "sync_measurements": True,
        }

        body = await self._post(
            path,
            json=data,
        )

        if body["status"] != _RESPONSE_STATUS_OK:
            raise NonOkResponseException(
                "Unknown response error. Check the log for more details.", path=path, data=data, body=body
            )

        return [HomeData(**home) for home in body["body"]["homes"]]

    async def async_get_home_measure(
        self,
        home_id: str,
        module_id: str,
        bridge: str,
        type: MeasurementType,
        scale: MeasurementScale,
        date_begin: datetime,
        date_end: datetime | None = None,
    ) -> HomeMeasure:
        """
        Get real time measurement data from the Netatmo API.

        On success, returns a list of measurements for provided measurement type. On error, throws an exception.
        """

        path = _GET_HOME_MEASURE_PATH
        data = {
            "app_identifier": _VAILLANT_APP_ID,
            "home": {
                "id": home_id,
                "modules": [{
                    "id": module_id,
                    "bridge": bridge,
                    "type": [type.value]
                }],
            },
            "scale": scale.value,
            "date_begin": round(date_begin.timestamp()),
        }

        if date_end is not None:
            data["date_end"] = round(date_end.timestamp())

        body = await self._post(
            path,
            json=data,
        )

        if body["status"] != _RESPONSE_STATUS_OK:
            raise NonOkResponseException(
                "Unknown response error. Check the log for more details.", path=path, data=data, body=body
            )

        return HomeMeasure(**body["body"]["home"])

    async def async_home_status(
        self,
        home_id: str,
    ) -> HomeStatus:
        """
        Get real time measurement data from the Netatmo API.

        On success, returns a list of measurements for provided measurement type. On error, throws an exception.
        """

        path = _HOME_STATUS_PATH
        data = {
            "app_identifier": _VAILLANT_APP_ID,
            "home_id": home_id,
            "device_types": [_DEVICE_TYPE]
        }

        body = await self._post(
            path,
            json=data,
        )

        if body["status"] != _RESPONSE_STATUS_OK:
            raise NonOkResponseException(
                "Unknown response error. Check the log for more details.", path=path, data=data, body=body
            )

        return HomeStatus(**body["body"]["home"])

    async def async_get_configs(
        self,
        home_id: str,
    ) -> HomeConfig:
        """
        Get real time measurement data from the Netatmo API.

        On success, returns a list of measurements for provided measurement type. On error, throws an exception.
        """

        path = _GET_CONFIGS_PATH
        data = {
            "app_identifier": _VAILLANT_APP_ID,
            "home_id": home_id,
        }

        body = await self._post(
            path,
            json=data,
        )

        if body["status"] != _RESPONSE_STATUS_OK:
            raise NonOkResponseException(
                "Unknown response error. Check the log for more details.", path=path, data=data, body=body
            )

        return HomeConfig(**body["body"]["home"])

    async def async_set_home_data(
        self,
        home_id: str,
        temperature_control_mode: TemperatureControlMode | None = None,
        therm_mode: ThermMode | None = None,
        therm_setpoint_default_duration: int | None = None,
    ) -> None:
        """
        Change the thermostat's system mode to the provided value.

        On success, returns nothing. On error, throws an exception.
        """

        path = _SET_HOME_DATA_PATH
        data = {
            "app_identifier": _VAILLANT_APP_ID,
            "home": {
                "id": home_id,
            },
        }

        if temperature_control_mode is not None:
            data["home"]["temperature_control_mode"] = temperature_control_mode.value

        if therm_mode is not None:
            data["home"]["therm_mode"] = therm_mode.value

        if therm_setpoint_default_duration is not None:
            data["home"]["therm_setpoint_default_duration"] = therm_setpoint_default_duration

        body = await self._post(
            path,
            json=data,
        )

        if body["status"] != _RESPONSE_STATUS_OK:
            raise NonOkResponseException(
                "Unknown response error. Check the log for more details.", path=path, data=data, body=body
            )

    async def async_switch_schedule(
        self,
        home_id: str,
        schedule_id: str,
        schedule_type: ScheduleType,
    ) -> None:
        """
        Change the thermostat's active schedule to the provided value.

        On success, returns nothing. On error, throws an exception.
        """

        path = _SWITCH_HOME_SCHEDULE_PATH
        data = {
            "app_identifier": _VAILLANT_APP_ID,
            "home_id": home_id,
            "schedule_id": schedule_id,
            "schedule_type": schedule_type.value,
        }

        body = await self._post(
            path,
            json=data,
        )

        if body["status"] != _RESPONSE_STATUS_OK:
            raise NonOkResponseException(
                "Unknown response error. Check the log for more details.", path=path, data=data, body=body
            )

    async def async_set_state_for_room(
        self,
        home_id: str,
        room_id: str,
        therm_setpoint_mode: ThermSetpointMode,
        therm_setpoint_temperature: float | None = None,
        therm_setpoint_end_time: datetime | None = None,
    ) -> None:
        """
        Activate or deactivate thermostat's minor mode, for the provided duration and temperature.

        On success, returns nothing. On error, throws an exception.
        """

        path = _SET_STATE_PATH
        data = {
            "app_identifier": _VAILLANT_APP_ID,
            "home": {
                "id": home_id,
                "rooms": [{
                    "id": room_id,
                    "therm_setpoint_mode": therm_setpoint_mode.value,
                }],
            },
        }

        endtime = self._get_setpoint_endtime(
            therm_setpoint_mode, therm_setpoint_end_time
        )
        if endtime is not None:
            data["home"]["rooms"][0]["therm_setpoint_end_time"] = endtime

        temp = self._get_setpoint_temp(
            therm_setpoint_mode, therm_setpoint_temperature)
        if temp is not None:
            data["home"]["rooms"][0]["therm_setpoint_temperature"] = temp

        body = await self._post(
            path,
            json=data,
        )

        if body["status"] != _RESPONSE_STATUS_OK:
            raise NonOkResponseException(
                "Unknown response error. Check the log for more details.", path=path, data=data, body=body
            )

    async def async_set_state_for_module(
        self,
        home_id: str,
        module_id: str,
        dhw_enabled: bool | None = None,
    ) -> None:
        """
        Activate or deactivate thermostat's minor mode, for the provided duration and temperature.

        On success, returns nothing. On error, throws an exception.
        """

        path = _SET_STATE_PATH
        data = {
            "app_identifier": _VAILLANT_APP_ID,
            "home": {
                "id": home_id,
                "modules": [{
                    "id": module_id,
                }],
            },
        }
        if dhw_enabled is not None:
            data["home"]["modules"][0]["dhw_enabled"] = dhw_enabled

        body = await self._post(
            path,
            json=data,
        )

        if body["status"] != _RESPONSE_STATUS_OK:
            raise NonOkResponseException(
                "Unknown response error. Check the log for more details.", path=path, data=data, body=body
            )

    async def async_set_configs_for_module(
        self,
        home_id: str,
        module_id: str,
        dhw_setpoint_temperature: int | None = None,
        dhw_always_on: bool | None = None,
    ) -> None:
        """
        Activate or deactivate thermostat's minor mode, for the provided duration and temperature.

        On success, returns nothing. On error, throws an exception.
        """

        path = _SET_CONFIGS_PATH
        data = {
            "app_identifier": _VAILLANT_APP_ID,
            "home": {
                "id": home_id,
                "modules": [{
                    "id": module_id,
                }],
            },
        }

        if dhw_setpoint_temperature is not None:
            data["home"]["modules"][0]["dhw_setpoint_temperature"] = dhw_setpoint_temperature

        if dhw_always_on is not None:
            data["home"]["modules"][0]["dhw_always_on"] = dhw_always_on

        body = await self._post(
            path,
            json=data,
        )

        if body["status"] != _RESPONSE_STATUS_OK:
            raise NonOkResponseException(
                "Unknown response error. Check the log for more details.", path=path, data=data, body=body
            )

    def _get_setpoint_endtime(
        self,
        therm_setpoint_mode: ThermSetpointMode,
        setpoint_endtime: datetime | None = None,
    ) -> int | None:
        if therm_setpoint_mode == ThermSetpointMode.HOME and setpoint_endtime is not None:
            raise UnsuportedArgumentsException(
                "Provided arguments for setting endtime are not valid.", therm_setpoint_mode=therm_setpoint_mode, setpoint_endtime=setpoint_endtime
            )

        if therm_setpoint_mode == ThermSetpointMode.MANUAL and setpoint_endtime is None:
            raise UnsuportedArgumentsException(
                "Provided arguments for setting endtime are not valid.", therm_setpoint_mode=therm_setpoint_mode, setpoint_endtime=setpoint_endtime
            )

        if setpoint_endtime is None:
            return None

        if setpoint_endtime <= now():
            raise UnsuportedArgumentsException(
                "Provided arguments for setting endtime are not valid.", therm_setpoint_mode=therm_setpoint_mode, setpoint_endtime=setpoint_endtime
            )

        return round(setpoint_endtime.timestamp())

    def _get_setpoint_temp(
        self,
        therm_setpoint_mode: ThermSetpointMode,
        setpoint_temp: float | None = None,
    ) -> float | None:
        if therm_setpoint_mode == ThermSetpointMode.HOME and setpoint_temp is not None:
            raise UnsuportedArgumentsException(
                "Provided arguments for setting endtime are not valid.", therm_setpoint_mode=therm_setpoint_mode, setpoint_temp=setpoint_temp
            )

        if therm_setpoint_mode == ThermSetpointMode.MANUAL and setpoint_temp is None:
            raise UnsuportedArgumentsException(
                "Provided arguments for setting endtime are not valid.", therm_setpoint_mode=therm_setpoint_mode, setpoint_temp=setpoint_temp
            )

        return setpoint_temp
