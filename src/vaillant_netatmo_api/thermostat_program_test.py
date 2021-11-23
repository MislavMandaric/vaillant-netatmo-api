import pytest

from datetime import datetime
from pytest_mock import MockerFixture

from vaillant_netatmo_api.thermostat import Program

@pytest.mark.parametrize(
    "current_time,expected_time_slot_index", 
    [
        # Monday
        (datetime(2021, 11, 22, 0, 0), 0),
        (datetime(2021, 11, 22, 0, 59), 0),
        (datetime(2021, 11, 22, 1, 0), 1),
        (datetime(2021, 11, 22, 1, 1), 1),
        (datetime(2021, 11, 22, 1, 59), 1),
        (datetime(2021, 11, 22, 2, 0), 2),
        (datetime(2021, 11, 22, 2, 1), 2),
        (datetime(2021, 11, 22, 23, 59), 2),
        # Tuesday
        (datetime(2021, 11, 23, 0, 0), 3),
        (datetime(2021, 11, 23, 0, 59), 3),
        (datetime(2021, 11, 23, 1, 0), 4),
        (datetime(2021, 11, 23, 1, 1), 4),
        (datetime(2021, 11, 23, 1, 59), 4),
        (datetime(2021, 11, 23, 2, 0), 5),
        (datetime(2021, 11, 23, 2, 1), 5),
        (datetime(2021, 11, 23, 23, 59), 5),
        # Wednesday
        (datetime(2021, 11, 24, 0, 0), 6),
        (datetime(2021, 11, 24, 0, 59), 6),
        (datetime(2021, 11, 24, 1, 0), 7),
        (datetime(2021, 11, 24, 1, 1), 7),
        (datetime(2021, 11, 24, 1, 59), 7),
        (datetime(2021, 11, 24, 2, 0), 8),
        (datetime(2021, 11, 24, 2, 1), 8),
        (datetime(2021, 11, 24, 23, 59), 8),
        # Thursday
        (datetime(2021, 11, 25, 0, 0), 9),
        (datetime(2021, 11, 25, 0, 59), 9),
        (datetime(2021, 11, 25, 1, 0), 10),
        (datetime(2021, 11, 25, 1, 1), 10),
        (datetime(2021, 11, 25, 1, 59), 10),
        (datetime(2021, 11, 25, 2, 0), 11),
        (datetime(2021, 11, 25, 2, 1), 11),
        (datetime(2021, 11, 25, 23, 59), 11),
        # Friday
        (datetime(2021, 11, 26, 0, 0), 12),
        (datetime(2021, 11, 26, 0, 59), 12),
        (datetime(2021, 11, 26, 1, 0), 13),
        (datetime(2021, 11, 26, 1, 1), 13),
        (datetime(2021, 11, 26, 1, 59), 13),
        (datetime(2021, 11, 26, 2, 0), 14),
        (datetime(2021, 11, 26, 2, 1), 14),
        (datetime(2021, 11, 26, 23, 59), 14),
        # Saturday
        (datetime(2021, 11, 27, 0, 0), 15),
        (datetime(2021, 11, 27, 0, 59), 15),
        (datetime(2021, 11, 27, 1, 0), 16),
        (datetime(2021, 11, 27, 1, 1), 16),
        (datetime(2021, 11, 27, 1, 59), 16),
        (datetime(2021, 11, 27, 2, 0), 17),
        (datetime(2021, 11, 27, 2, 1), 17),
        (datetime(2021, 11, 27, 23, 59), 17),
        # Sunday
        (datetime(2021, 11, 28, 0, 0), 18),
        (datetime(2021, 11, 28, 0, 59), 18),
        (datetime(2021, 11, 28, 1, 0), 19),
        (datetime(2021, 11, 28, 1, 1), 19),
        (datetime(2021, 11, 28, 1, 59), 19),
        (datetime(2021, 11, 28, 2, 0), 20),
        (datetime(2021, 11, 28, 2, 1), 20),
        (datetime(2021, 11, 28, 23, 59), 20),
        # Monday
        (datetime(2021, 11, 29, 0, 0), 0),
        (datetime(2021, 11, 29, 0, 59), 0),
        (datetime(2021, 11, 29, 1, 0), 1),
        (datetime(2021, 11, 29, 1, 1), 1),
        (datetime(2021, 11, 29, 1, 59), 1),
        (datetime(2021, 11, 29, 2, 0), 2),
        (datetime(2021, 11, 29, 2, 1), 2),
        (datetime(2021, 11, 29, 23, 59), 2),
    ]
)
@pytest.mark.asyncio
class TestProgram:
    async def test_get_active_zone__timetable_with_three_slots_per_day__returns_correct_index_around_bounderies(self, current_time: datetime, expected_time_slot_index: int, mocker: MockerFixture):
        mocker.patch("vaillant_netatmo_api.thermostat.now", return_value=current_time)

        program = Program(
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

        time_slot_index = program.get_active_time_slot_index()

        assert time_slot_index == expected_time_slot_index
