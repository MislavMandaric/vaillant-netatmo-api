"""Module HTTP communication with the Netatmo API."""

from .auth import AuthClient
from .errors import BadResponseException, UnsuportedArgumentsException
from .thermostat import (
    Device,
    Measured,
    Module,
    Setpoint,
    SetpointMode,
    SystemMode,
    ThermostatClient,
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
    "serialize_token",
    "deserialize_token",
]
