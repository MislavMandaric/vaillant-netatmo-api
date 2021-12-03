import pytest

from datetime import datetime

from pytest_mock import MockerFixture

from vaillant_netatmo_api.thermostat import Program

@pytest.mark.parametrize(
    "current_time,expected_active_zone_id", 
    [
        # Monday
        (datetime(2021, 11, 22, 0, 0), 1),
        (datetime(2021, 11, 22, 0, 59), 1),
        (datetime(2021, 11, 22, 1, 0), 0),
        (datetime(2021, 11, 22, 1, 1), 0),
        (datetime(2021, 11, 22, 1, 59), 0),
        (datetime(2021, 11, 22, 2, 0), 2),
        (datetime(2021, 11, 22, 2, 1), 2),
        (datetime(2021, 11, 22, 23, 59), 2),
        # Tuesday
        (datetime(2021, 11, 23, 0, 0), 1),
        (datetime(2021, 11, 23, 0, 59), 1),
        (datetime(2021, 11, 23, 1, 0), 0),
        (datetime(2021, 11, 23, 1, 1), 0),
        (datetime(2021, 11, 23, 1, 59), 0),
        (datetime(2021, 11, 23, 2, 0), 2),
        (datetime(2021, 11, 23, 2, 1), 2),
        (datetime(2021, 11, 23, 23, 59), 2),
        # Wednesday
        (datetime(2021, 11, 24, 0, 0), 1),
        (datetime(2021, 11, 24, 0, 59), 1),
        (datetime(2021, 11, 24, 1, 0), 0),
        (datetime(2021, 11, 24, 1, 1), 0),
        (datetime(2021, 11, 24, 1, 59), 0),
        (datetime(2021, 11, 24, 2, 0), 2),
        (datetime(2021, 11, 24, 2, 1), 2),
        (datetime(2021, 11, 24, 23, 59), 2),
        # Thursday
        (datetime(2021, 11, 25, 0, 0), 1),
        (datetime(2021, 11, 25, 0, 59), 1),
        (datetime(2021, 11, 25, 1, 0), 0),
        (datetime(2021, 11, 25, 1, 1), 0),
        (datetime(2021, 11, 25, 1, 59), 0),
        (datetime(2021, 11, 25, 2, 0), 2),
        (datetime(2021, 11, 25, 2, 1), 2),
        (datetime(2021, 11, 25, 23, 59), 2),
        # Friday
        (datetime(2021, 11, 26, 0, 0), 1),
        (datetime(2021, 11, 26, 0, 59), 1),
        (datetime(2021, 11, 26, 1, 0), 0),
        (datetime(2021, 11, 26, 1, 1), 0),
        (datetime(2021, 11, 26, 1, 59), 0),
        (datetime(2021, 11, 26, 2, 0), 2),
        (datetime(2021, 11, 26, 2, 1), 2),
        (datetime(2021, 11, 26, 23, 59), 2),
        # Saturday
        (datetime(2021, 11, 27, 0, 0), 1),
        (datetime(2021, 11, 27, 0, 59), 1),
        (datetime(2021, 11, 27, 1, 0), 0),
        (datetime(2021, 11, 27, 1, 1), 0),
        (datetime(2021, 11, 27, 1, 59), 0),
        (datetime(2021, 11, 27, 2, 0), 2),
        (datetime(2021, 11, 27, 2, 1), 2),
        (datetime(2021, 11, 27, 23, 59), 2),
        # Sunday
        (datetime(2021, 11, 28, 0, 0), 1),
        (datetime(2021, 11, 28, 0, 59), 1),
        (datetime(2021, 11, 28, 1, 0), 0),
        (datetime(2021, 11, 28, 1, 1), 0),
        (datetime(2021, 11, 28, 1, 59), 0),
        (datetime(2021, 11, 28, 2, 0), 2),
        (datetime(2021, 11, 28, 2, 1), 2),
        (datetime(2021, 11, 28, 23, 59), 2),
        # Monday
        (datetime(2021, 11, 29, 0, 0), 1),
        (datetime(2021, 11, 29, 0, 59), 1),
        (datetime(2021, 11, 29, 1, 0), 0),
        (datetime(2021, 11, 29, 1, 1), 0),
        (datetime(2021, 11, 29, 1, 59), 0),
        (datetime(2021, 11, 29, 2, 0), 2),
        (datetime(2021, 11, 29, 2, 1), 2),
        (datetime(2021, 11, 29, 23, 59), 2),
    ]
)
@pytest.mark.asyncio
class TestProgramForZones:
    async def test_get_active_zone__timetable_with_three_slots_per_day__returns_correct_index_around_bounderies(self, current_time: datetime, expected_active_zone_id: int, mocker: MockerFixture):
        mocker.patch("vaillant_netatmo_api.thermostat.now", return_value=current_time)

        program = Program(
            zones=[
                {"id": 0},
                {"id": 1},
                {"id": 2},
            ],
            timetable=[
                {"id": 1, "m_offset": 0},
                {"id": 0, "m_offset": 60},
                {"id": 2, "m_offset": 120},
                {"id": 1, "m_offset": 1440},
                {"id": 0, "m_offset": 1500},
                {"id": 2, "m_offset": 1560},
                {"id": 1, "m_offset": 2880},
                {"id": 0, "m_offset": 2940},
                {"id": 2, "m_offset": 3000},
                {"id": 1, "m_offset": 4320},
                {"id": 0, "m_offset": 4380},
                {"id": 2, "m_offset": 4440},
                {"id": 1, "m_offset": 5760},
                {"id": 0, "m_offset": 5820},
                {"id": 2, "m_offset": 5880},
                {"id": 1, "m_offset": 7200},
                {"id": 0, "m_offset": 7260},
                {"id": 2, "m_offset": 7320},
                {"id": 1, "m_offset": 8640},
                {"id": 0, "m_offset": 8700},
                {"id": 2, "m_offset": 8760},
            ],
        )

        active_zone = program.get_active_zone()

        assert active_zone.id == expected_active_zone_id

@pytest.mark.asyncio
class TestProgramForTimeslots:
    async def test_get_timeslots_for_today__timetable_with_alternating_zones__returns_monday_without_padding(self, mocker: MockerFixture):
        monday = datetime(2021, 11, 22, 1, 0)

        mocker.patch("vaillant_netatmo_api.thermostat.now", return_value=monday)

        program = Program(
            timetable=[
                {"id": 2, "m_offset": 0},
                {"id": 0, "m_offset": 60},
                {"id": 1, "m_offset": 120},
                {"id": 0, "m_offset": 1500},
                {"id": 2, "m_offset": 1560},
                {"id": 0, "m_offset": 2940},
                {"id": 1, "m_offset": 3000},
            ],
        )

        time_slots = program.get_timeslots_for_today()

        assert len(time_slots) == 3
        assert time_slots[0].id == 2
        assert time_slots[0].m_offset == 0
        assert time_slots[1].id == 0
        assert time_slots[1].m_offset == 60
        assert time_slots[2].id == 1
        assert time_slots[2].m_offset == 120

    async def test_get_timeslots_for_today__timetable_with_alternating_zones__returns_other_days_with_padding(self, mocker: MockerFixture):
        tuesday = datetime(2021, 11, 23, 1, 0)

        mocker.patch("vaillant_netatmo_api.thermostat.now", return_value=tuesday)

        program = Program(
            timetable=[
                {"id": 2, "m_offset": 0},
                {"id": 0, "m_offset": 60},
                {"id": 1, "m_offset": 120},
                {"id": 0, "m_offset": 1500},
                {"id": 2, "m_offset": 1560},
                {"id": 0, "m_offset": 2940},
                {"id": 1, "m_offset": 3000},
            ],
        )

        time_slots = program.get_timeslots_for_today()

        assert len(time_slots) == 3
        assert time_slots[0].id == 1
        assert time_slots[0].m_offset == 1440
        assert time_slots[1].id == 0
        assert time_slots[1].m_offset == 1500
        assert time_slots[2].id == 2
        assert time_slots[2].m_offset == 1560
