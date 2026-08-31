"""Test the eBUS status attribute of a device."""

from vaillant_netatmo_api.thermostat import Device, EbusStatus


class TestDeviceEbusStatus:
    def test_device__ebus_status_reported__is_parsed(self) -> None:
        device = Device(
            **{
                "_id": "70:ee:50:00:00:00",
                "system_mode": "winter",
                "ebus_status": {
                    "ebus_error": False,
                    "boiler_error": False,
                    "maintenance_status": True,
                    "refill_water": True,
                    "emf_avail": False,
                },
                "dhw_enabled": True,
            }
        )

        assert device.ebus_status.maintenance_status is True
        assert device.ebus_status.refill_water is True
        assert device.ebus_status.boiler_error is False
        assert device.dhw_enabled is True

    def test_device__ebus_status_missing__defaults_to_no_faults(self) -> None:
        device = Device(**{"_id": "70:ee:50:00:00:00", "system_mode": "winter"})

        assert device.ebus_status == EbusStatus()
        assert device.ebus_status.refill_water is False
        assert device.dhw_enabled is False

    def test_device__ebus_status_has_unknown_key__is_ignored(self) -> None:
        device = Device(**{"_id": "70:ee:50:00:00:00",
                "system_mode": "winter",
                           "ebus_status": {"refill_water": True, "future_flag": True}})

        assert device.ebus_status.refill_water is True
