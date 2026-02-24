from __future__ import annotations

from enum import Enum
from datetime import datetime, time
from .time import now

_SETPOINT_DEFAULT_DURATION_MINS = 120


class HomeData:
    """Home model representing a home in Vaillant system."""

    def __init__(
        self,
        id: str | None = None,
        name: str = "",
        temperature_control_mode: str | None = None,
        therm_mode: str | None = None,
        therm_setpoint_default_duration: int = _SETPOINT_DEFAULT_DURATION_MINS,
        anticipation: bool = False,
        therm_heating_priority: str | None = None,
        cooling_mode: str | None = None,
        rooms: list[dict] = [],
        modules: list[dict] = [],
        therm_schedules: list[dict] = [],
        **kwargs,
    ) -> None:
        """Create new home model."""

        self.id = id
        self.name = name
        self.temperature_control_mode = TemperatureControlMode(
            temperature_control_mode)
        self.therm_mode = ThermMode(therm_mode)
        self.therm_setpoint_default_duration = therm_setpoint_default_duration
        self.anticipation = anticipation
        self.therm_heating_priority = therm_heating_priority
        self.cooling_mode = ThermMode(cooling_mode)
        self.rooms = [RoomData(**room) for room in rooms]
        self.modules = [ModuleData(**module) for module in modules]
        self.therm_schedules = [ScheduleData(**schedule)
                                for schedule in therm_schedules]

    def __eq__(self, other: HomeData):
        if not isinstance(other, HomeData):
            return False

        return (
            self.id == other.id
            and len(self.rooms) == len(other.rooms)
            and all([False for i, j in zip(self.rooms, other.rooms) if i != j])
            and len(self.modules) == len(other.modules)
            and all([False for i, j in zip(self.modules, other.modules) if i != j])
            and len(self.therm_schedules) == len(other.therm_schedules)
            and all([False for i, j in zip(self.therm_schedules, other.therm_schedules) if i != j])
        )


class RoomData:
    """Room model representing a room in a home for Vaillant system."""

    def __init__(
        self,
        id: str | None = None,
        type: str = "",
        module_ids: list[str] = [],
        modules: list[str] = [],
        therm_relay: str = "",
        **kwargs,
    ) -> None:
        """Create new room model."""

        self.id = id
        self.type = type
        self.module_ids = module_ids
        self.modules = modules
        self.therm_relay = therm_relay

    def __eq__(self, other: RoomData):
        if not isinstance(other, RoomData):
            return False

        return (
            self.id == other.id
        )


class ModuleData:
    """Module model representing a module in a home for Vaillant system."""

    def __init__(
        self,
        id: str | None = None,
        type: str = "",
        **kwargs,
    ) -> None:
        """Create new module model."""

        self.id = id
        self.type = type

    def __eq__(self, other: ModuleData):
        if not isinstance(other, ModuleData):
            return False

        return (
            self.id == other.id
        )


class NAVaillantModuleData(ModuleData):
    """Module model representing a module in a home for Vaillant system."""

    def __init__(
        self,
        id: str | None = None,
        type: str = "",
        subtype: str = "",
        modules_bridged: list[str] = [],
        oem_serial: str = "",
        dhw_control: str = "",
        **kwargs,
    ) -> None:
        """Create new module model."""

        super().__init__(id, type)

        self.subtype = subtype
        self.modules_bridged = modules_bridged
        self.oem_serial = oem_serial
        self.dhw_control = dhw_control


class NAThermVaillantModuleData(ModuleData):
    """Module model representing a module in a home for Vaillant system."""

    def __init__(
        self,
        id: str | None = None,
        type: str = "",
        name: str = "",
        room_id: str = "",
        bridge: str = "",
        **kwargs,
    ) -> None:
        """Create new module model."""

        super().__init__(id, type)

        self.name = name
        self.room_id = room_id
        self.bridge = bridge


class ScheduleData:
    """Schedule attribute representing a schedule for a thermostat."""

    def __init__(
        self,
        id: str | None = None,
        type: str = "",
        name: str = "",
        default: bool = False,
        away_temp: int = 0,
        hg_temp: int = 0,
        selected: bool = False,
        zones: list[dict] = [],
        timetable: list[dict] = [],
        **kwargs,
    ) -> None:
        """Create new program model."""

        self.id = id
        self.type = type
        self.name = name
        self.default = default
        self.away_temp = away_temp
        self.hg_temp = hg_temp
        self.selected = selected
        self.zones = [Zone(**zone) for zone in zones]
        self.timetable = [TimeSlot(**time_slot) for time_slot in timetable]

    def get_active_zone(self) -> Zone | None:
        """Returns a currently active zone for a program."""

        zone_id = 0
        for time_slot in self.timetable:
            if not time_slot.is_already_started:
                break
            zone_id = time_slot.zone_id

        for zone in self.zones:
            if zone.id == zone_id:
                return zone

        return None

    def get_timeslots_for_today(self) -> list[TimeSlot]:
        """
        Returns a list of time slots which are defined for today.
        """

        n = now()

        time_slots = []
        previous_time_slot_zone_id = 0
        for time_slot in self.timetable:
            if time_slot.day == n.weekday():
                if len(time_slots) == 0 and time_slot.time != time(0, 0):
                    time_slots.append(
                        TimeSlot(
                            previous_time_slot_zone_id,
                            time_slot.day * 1440,
                        )
                    )
                time_slots.append(time_slot)
            previous_time_slot_zone_id = time_slot.zone_id

        return time_slots


class HomeMeasure:
    """Home model representing a home in Vaillant system."""

    def __init__(
        self,
        id: str | None = None,
        modules: list[dict] = [],
        **kwargs,
    ) -> None:
        """Create new home model."""

        self.id = id
        self.modules = [ModuleMeasure(**module) for module in modules]

    def __eq__(self, other: HomeMeasure):
        if not isinstance(other, HomeMeasure):
            return False

        return (
            self.id == other.id
            and len(self.modules) == len(other.modules)
            and all([False for i, j in zip(self.modules, other.modules) if i != j])
        )


class ModuleMeasure:
    """Home model representing a home in Vaillant system."""

    def __init__(
        self,
        id: str | None = None,
        bridge: str = "",
        measures: list[dict] = [],
        **kwargs,
    ) -> None:
        """Create new home model."""

        self.id = id
        self.bridge = bridge
        self.measures = [Measure(**measure) for measure in measures]

    def __eq__(self, other: ModuleMeasure):
        if not isinstance(other, ModuleMeasure):
            return False

        return (
            self.id == other.id
            and len(self.measures) == len(other.measures)
            and all([False for i, j in zip(self.measures, other.measures) if i != j])
        )


class HomeStatus:
    """Home model representing a home in Vaillant system."""

    def __init__(
        self,
        id: str | None = None,
        rooms: list[dict] = [],
        modules: list[dict] = [],
        **kwargs,
    ) -> None:
        """Create new home model."""

        self.id = id
        self.rooms = [RoomStatus(**room) for room in rooms]
        self.modules = [ModuleStatus(**module) for module in modules]

    def __eq__(self, other: HomeMeasure):
        if not isinstance(other, HomeMeasure):
            return False

        return (
            self.id == other.id
            and len(self.modules) == len(other.modules)
            and all([False for i, j in zip(self.modules, other.modules) if i != j])
        )


class RoomStatus:
    """Module model representing a module in a home for Vaillant system."""

    def __init__(
        self,
        id: str | None = None,
        anticipating: bool = False,
        reachable: bool = False,
        therm_measured_temperature: float | None = None,
        therm_setpoint_mode: str = "",
        therm_setpoint_start_time: int | None = None,
        therm_setpoint_temperature: float | None = None,
        ** kwargs,
    ) -> None:
        """Create new module model."""

        self.id = id
        self.anticipating = anticipating
        self.reachable = reachable
        self.therm_measured_temperature = therm_measured_temperature
        self.therm_setpoint_mode = therm_setpoint_mode
        self.therm_setpoint_start_time = therm_setpoint_start_time
        self.therm_setpoint_temperature = therm_setpoint_temperature

    def __eq__(self, other: ModuleStatus):
        if not isinstance(other, ModuleStatus):
            return False

        return (
            self.id == other.id
        )


class ModuleStatus:
    """Module model representing a module in a home for Vaillant system."""

    def __init__(
        self,
        id: str | None = None,
        type: str = "",
        **kwargs,
    ) -> None:
        """Create new module model."""

        self.id = id
        self.type = type

    def __eq__(self, other: ModuleStatus):
        if not isinstance(other, ModuleStatus):
            return False

        return (
            self.id == other.id
        )


class NAVaillantModuleStatus(ModuleStatus):
    """Module model representing a module in a home for Vaillant system."""

    def __init__(
        self,
        id: str | None = None,
        type: str = "",
        dhw_enabled: bool = False,
        ebus_error: bool = False,
        emf_avail: bool = False,
        outdoor_temperature: int | None = None,
        rf_strength: int | None = None,
        wifi_strength: int | None = None,
        **kwargs,
    ) -> None:
        """Create new module model."""

        super().__init__(id, type)

        self.dhw_enabled = dhw_enabled
        self.ebus_error = ebus_error
        self.emf_avail = emf_avail
        self.outdoor_temperature = outdoor_temperature
        self.rf_strength = rf_strength
        self.wifi_strength = wifi_strength


class NAThermVaillantModuleStatus(ModuleStatus):
    """Module model representing a module in a home for Vaillant system."""

    def __init__(
        self,
        id: str | None = None,
        type: str = "",
        battery_level: int | None = None,
        battery_percent: int | None = None,
        boiler_status: bool = False,
        reachable: bool = False,
        rf_strength: int | None = None,
        battery_state: str = "",
        ** kwargs,
    ) -> None:
        """Create new module model."""

        super().__init__(id, type)

        self.battery_level = battery_level
        self.battery_percent = battery_percent
        self.boiler_status = boiler_status
        self.reachable = reachable
        self.rf_strength = rf_strength
        self.battery_state = battery_state


class HomeConfig:

    def __init__(
        self,
        id: str | None = None,
        modules: list[dict] = [],
        **kwargs,
    ) -> None:
        """Create new home model."""

        self.id = id
        self.modules = [ModuleConfig(**module) for module in modules]

    def __eq__(self, other: HomeConfig):
        if not isinstance(other, HomeConfig):
            return False

        return (
            self.id == other.id
            and len(self.modules) == len(other.modules)
            and all([False for i, j in zip(self.modules, other.modules) if i != j])
        )


class ModuleConfig:
    """Module model representing a module in a home for Vaillant system."""

    def __init__(
        self,
        id: str | None = None,
        type: str = "",
        rf_stats: bool = False,
        dhw_always_on: bool = False,
        dhw_setpoint_temperature: int | None = None,
        dhw_temperature_max: int | None = None,
        dhw_temperature_min: int | None = None,
        **kwargs,
    ) -> None:
        """Create new module model."""

        self.id = id
        self.type = type
        self.rf_stats = rf_stats
        self.dhw_always_on = dhw_always_on
        self.dhw_setpoint_temperature = dhw_setpoint_temperature
        self.dhw_temperature_max = dhw_temperature_max
        self.dhw_temperature_min = dhw_temperature_min

    def __eq__(self, other: ModuleConfig):
        if not isinstance(other, ModuleConfig):
            return False

        return (
            self.id == other.id
        )


class Zone:
    """Zone attribute representing a zone profile which defines how thermostat behaves in a given time slot."""

    def __init__(
        self,
        id: int | None = None,
        type: int = 0,
        rooms_temp: list[dict] = [],
        **kwargs,
    ) -> None:
        """Create new zone attribute."""

        self.id = id
        self.type = type
        self.rooms_temp = [RoomTemp(**room_temp) for room_temp in rooms_temp]


class RoomTemp:

    def __init__(
        self,
        room_id: int | None = None,
        temp: int = 0,
        **kwargs,
    ) -> None:
        """RoomTemp."""

        self.room_id = room_id
        self.temp = temp


class TimeSlot:
    """TimeSlot attribute representing one slot of a timetable schedule."""

    def __init__(
        self,
        zone_id: int | None = None,
        m_offset: int = 0,
        **kwargs,
    ) -> None:
        """Create new time slot attribute."""

        self.zone_id = zone_id
        self.m_offset = m_offset

    @property
    def time(self) -> time:
        """Returns time instance representing the offset defined for this time slot."""

        daily_offset = self.m_offset % 1440

        return time(daily_offset // 60, daily_offset % 60)

    @property
    def day(self) -> int:
        """Returns a day for which this time slot is defined, using the same format as datetime.weekday()."""

        return self.m_offset // 1440

    @property
    def is_already_started(self) -> bool:
        n = now()

        if self.day < n.weekday():
            return True
        elif self.day == n.weekday() and self.time <= n.time():
            return True
        else:
            return False


class Measure:
    """Measure attribute representing a one measurement of thermostat module."""

    def __init__(
        self,
        beg_time: int | None = None,
        step_time: int | None = None,
        value: list[list[float]] = [],
        **kwargs,
    ) -> None:
        """Create new measurement item."""

        self.beg_time = beg_time
        self.step_time = step_time
        self.value = [
            value_item for inner_list in value for value_item in inner_list
        ]

    def __eq__(self, other: MeasurementItem):
        if not isinstance(other, MeasurementItem):
            return False

        return (
            self.beg_time == other.beg_time
            and self.step_time == other.step_time
            and len(self.value) == len(other.value)
            and all([False for i, j in zip(self.value, other.value) if i != j])
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


class ScheduleType(Enum):
    """"""

    THERM = "therm"
    EVENT = "event"


class MeasurementType(Enum):
    """MeasurementType enumeration representing possible measurements of the thermostat."""

    TEMPERATURE = "temperature"
    SETPOINT_TEMPERATURE = "sp_temperature"
    SUM_BOILER_ON = "sum_boiler_on"
    SUM_BOILER_OFF = "sum_boiler_off"

    SUM_ENERGY_GAS_HEATING = "sum_energy_gaz_heating"
    SUM_ENERGY_GAS_WATER = "sum_energy_gaz_hot_water"
    SUM_ENERGY_ELEC_HEATING = "sum_energy_elec_heating"
    SUM_ENERGY_ELEC_WATER = "sum_energy_elec_hot_water"


class MeasurementScale(Enum):
    """MeasurementScale enumeration representing possible scale options for measurements of the thermostat."""

    MAX = "max"
    FIVE_MINS = "5min"
    HALF_HOUR = "30min"
    HOUR = "1hour"
    THREE_HOURS = "3hours"
    SIX_HOURS = "6hours"
    DAY = "1day"
    WEEK = "1week"
    MONTH = "1month"
