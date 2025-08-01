from __future__ import annotations

from enum import Enum


class Home:
    """Home model representing a home in Vaillant system."""

    def __init__(
        self,
        id: str | None = None,
        name: str = "",
        rooms: list[dict] = [],
        **kwargs,
    ) -> None:
        """Create new home model."""

        self.id = id
        self.name = name
        self.rooms = [Room(**room) for room in rooms]

    def __eq__(self, other: Home):
        if not isinstance(other, Home):
            return False

        return (
            self.id == other.id
            and len(self.rooms) == len(other.rooms)
            and all([False for i, j in zip(self.rooms, other.rooms) if i != j])
        )


class Room:
    """Room model representing a room in a home for Vaillant system."""

    def __init__(
        self,
        id: str | None = None,
        **kwargs,
    ) -> None:
        """Create new room model."""

        self.id = id

    def __eq__(self, other: Room):
        if not isinstance(other, Room):
            return False

        return (
            self.id == other.id
        )


class TemperatureControlMode(Enum):
    """TemperatureControlMode enumeration representing possible system modes of the thermostat."""

    HEATING = "heating"
    COOLING = "cooling"


class ThermMode(Enum):
    """ThermMode enumeration representing possible system modes of the thermostat."""

    HG = "hg"
    SCHEDULE = "schedule"
    AWAY = "away"


class ThermSetpointMode(Enum):
    """ThermSetpointMode enumeration representing possible system modes of the thermostat."""

    MANUAL = "manual"
    HOME = "home"
