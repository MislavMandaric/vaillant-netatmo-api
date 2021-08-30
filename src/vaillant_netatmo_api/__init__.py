"""Module HTTP communication with the Netatmo API."""

from .auth import AuthClient, auth_client
from .errors import BadResponseException, UnsuportedArgumentsException
from .thermostat import (
    Device,
    Measured,
    Module,
    Setpoint,
    SetpointMode,
    SystemMode,
    ThermostatClient,
    thermostat_client,
)
from .token import deserialize_token, serialize_token

__all__ = [
    "AuthClient",
    "ThermostatClient",
    "BadResponseException",
    "UnsuportedArgumentsException",
    "Device",
    "Module",
    "Setpoint",
    "Measured",
    "SystemMode",
    "SetpointMode",
    "auth_client",
    "thermostat_client",
    "serialize_token",
    "deserialize_token",
]
