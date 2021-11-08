"""Module containing a ThermostatClient for the Netatmo API."""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime
from enum import Enum
from typing import AsyncGenerator, Callable

from httpx import AsyncClient

from .base import BaseClient
from .errors import NonOkResponseException, UnsuportedArgumentsException
from .thermostat_auth import ThermostatAuth
from .token import Token, TokenStore

_GET_THERMOSTATS_DATA_PATH = "api/getthermostatsdata"
_SET_SYSTEM_MODE_PATH = "api/setsystemmode"
_SET_MINOR_MODE_PATH = "api/setminormode"
_VAILLANT_DEVICE_TYPE = "NAVaillant"
_RESPONSE_STATUS_OK = "ok"
_SETPOINT_DEFAULT_DURATION_MINS = 120


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

    async def async_get_thermostats_data(self) -> list[Device]:
        """
        Get thermostat data from the Netatmo API.

        On success, returns a list of thermostat devices with their modules. On error, throws an exception.
        """

        path = _GET_THERMOSTATS_DATA_PATH
        data = {"device_type": _VAILLANT_DEVICE_TYPE}

        body = await self._post(
            path,
            data=data,
        )

        if body["status"] != _RESPONSE_STATUS_OK:
            raise NonOkResponseException("Unknown response error. Check the log for more details.", path=path, data=data, body=body)

        return [Device(**device) for device in body["body"]["devices"]]

    async def async_set_system_mode(
        self, device_id: str, module_id: str, system_mode: SystemMode
    ) -> None:
        """
        Change the thermostat's system mode to the provided value.

        On success, returns nothing. On error, throws an exception.
        """

        path = _SET_SYSTEM_MODE_PATH
        data = {
            "device_id": device_id,
            "module_id": module_id,
            "system_mode": system_mode.value,
        }

        body = await self._post(
            path,
            data=data,
        )

        if body["status"] != _RESPONSE_STATUS_OK:
            raise NonOkResponseException("Unknown response error. Check the log for more details.", path=path, data=data, body=body)

    async def async_set_minor_mode(
        self,
        device_id: str,
        module_id: str,
        setpoint_mode: SetpointMode,
        activate: bool,
        setpoint_endtime: datetime | None = None,
        setpoint_temp: float | None = None,
    ) -> None:
        """
        Activate or deactivate thermostat's minor mode, for the provided duration and temperature.

        On success, returns nothing. On error, throws an exception.
        """

        path = _SET_MINOR_MODE_PATH
        data = {
            "device_id": device_id,
            "module_id": module_id,
            "setpoint_mode": setpoint_mode.value,
            "activate": activate,
        }

        endtime = self._get_setpoint_endtime(setpoint_mode, activate, setpoint_endtime)
        if endtime is not None:
            data["setpoint_endtime"] = endtime

        temp = self._get_setpoint_temp(setpoint_mode, activate, setpoint_temp)
        if temp is not None:
            data["setpoint_temp"] = temp

        body = await self._post(
            path,
            data=data,
        )

        if body["status"] != _RESPONSE_STATUS_OK:
            raise NonOkResponseException("Unknown response error. Check the log for more details.", path=path, data=data, body=body)

    def _get_setpoint_endtime(
        self, 
        setpoint_mode: SetpointMode,
        activate: bool,
        setpoint_endtime: datetime | None = None,
    ) -> int | None:
        if not activate:
            if setpoint_endtime is not None:
                raise UnsuportedArgumentsException("Provided arguments for setting endtime are not valid.", setpoint_mode=setpoint_mode, activate=activate, setpoint_endtime=setpoint_endtime)
            return None
        else:
            if setpoint_endtime is None:
                if setpoint_mode == SetpointMode.MANUAL or setpoint_mode == SetpointMode.HWB:
                    raise UnsuportedArgumentsException("Provided arguments for setting endtime are not valid.", setpoint_mode=setpoint_mode, activate=activate, setpoint_endtime=setpoint_endtime)
                return None
            else:
                if setpoint_endtime <= datetime.now():
                    raise UnsuportedArgumentsException("Provided arguments for setting endtime are not valid.", setpoint_mode=setpoint_mode, activate=activate, setpoint_endtime=setpoint_endtime)
                return round(setpoint_endtime.timestamp())

    def _get_setpoint_temp(
        self, 
        setpoint_mode: SetpointMode,
        activate: bool,
        setpoint_temp: float | None = None,
    ) -> float | None:
        if not activate:
            if setpoint_temp is not None:
                raise UnsuportedArgumentsException("Provided arguments for setting temp are not valid.", setpoint_mode=setpoint_mode, activate=activate, setpoint_temp=setpoint_temp)
            return None
        else:
            if setpoint_temp is None:
                if setpoint_mode == SetpointMode.MANUAL:
                    raise UnsuportedArgumentsException("Provided arguments for setting temp are not valid.", setpoint_mode=setpoint_mode, activate=activate, setpoint_temp=setpoint_temp)
                return None
            else:
                if setpoint_mode != SetpointMode.MANUAL:
                    raise UnsuportedArgumentsException("Provided arguments for setting temp are not valid.", setpoint_mode=setpoint_mode, activate=activate, setpoint_temp=setpoint_temp)
                return setpoint_temp


class Device:
    """Device model representing a Vaillant boiler. Contains multiple modules."""

    def __init__(
        self,
        _id: str | None = None,
        type: str = "",
        station_name: str = "",
        firmware: int = 0,
        system_mode: str | None = None,
        setpoint_default_duration: int = _SETPOINT_DEFAULT_DURATION_MINS,
        setpoint_hwb: dict = {},
        modules: list[dict] = [],
        **kwargs,
    ) -> None:
        """Create new device model."""

        self.id = _id
        self.type = type
        self.station_name = station_name
        self.firmware = firmware
        self.system_mode = SystemMode(system_mode)
        self.setpoint_default_duration = setpoint_default_duration
        self.setpoint_hwb = Setpoint(**setpoint_hwb)
        self.modules = [Module(**module) for module in modules]

    def __eq__(self, other: Device):
        if (not isinstance(other, Device)):
            return False
        
        return self.id == other.id and \
            self.type == other.type and \
            self.station_name == other.station_name and \
            self.firmware == other.firmware and \
            len(self.modules) == len(other.modules) and \
            all([False for i, j in zip(self.modules, other.modules) if i != j])

class Module:
    """Module model representing a Vaillant thermostat."""

    def __init__(
        self,
        _id: str | None = None,
        type: str = "",
        module_name: str = "",
        firmware: int = 0,
        battery_percent: int = 0,
        setpoint_away: dict = {},
        setpoint_manual: dict = {},
        measured: dict = {},
        **kwargs,
    ) -> None:
        """Create new module model."""

        self.id = _id
        self.type = type
        self.module_name = module_name
        self.firmware = firmware
        self.battery_percent = battery_percent
        self.setpoint_away = Setpoint(**setpoint_away)
        self.setpoint_manual = Setpoint(**setpoint_manual)
        self.measured = Measured(**measured)

    def __eq__(self, other: Module):
        if (not isinstance(other, Module)):
            return False
        
        return self.id == other.id and \
            self.type == other.type and \
            self.module_name == other.module_name and \
            self.firmware == other.firmware and \
            self.battery_percent == other.battery_percent


class Setpoint:
    """Setpoint attribute representing a minor mode and its status."""

    def __init__(
        self,
        setpoint_activate: bool = False,
        **kwargs,
    ) -> None:
        """Create new setpoint attribute."""

        self.setpoint_activate = setpoint_activate


class Measured:
    """Measured attribute representing a thermostat measurement."""

    def __init__(
        self,
        temperature: float | None = None,
        setpoint_temp: float | None = None,
        est_setpoint_temp: float | None = None,
        **kwargs,
    ) -> None:
        """Create new measured attribute."""

        self.temperature = temperature
        self.setpoint_temp = setpoint_temp
        self.est_setpoint_temp = est_setpoint_temp


class SystemMode(Enum):
    """SystemMode enumeration representing possible system modes of the thermostat."""

    WINTER = "winter"
    SUMMER = "summer"
    FROSTGUARD = "frostguard"


class SetpointMode(Enum):
    """SetpointMode enumeration representing possible minor modes of the thermostat."""

    MANUAL = "manual"
    AWAY = "away"
    HWB = "hwb"
