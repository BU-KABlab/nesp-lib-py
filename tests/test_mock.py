import pytest
from nesp_lib.mock import Pump
from nesp_lib.pumping_direction import PumpingDirection
from nesp_lib.status import Status


def test_mock_pump_initialization():
    """Test that the mock pump initializes correctly"""
    pump = Pump()
    assert pump.address == Pump.ADDRESS_DEFAULT
    assert pump.model_number is not None
    assert pump.firmware_version is not None


def test_mock_pump_syringe_diameter():
    """Test syringe diameter getter and setter"""
    pump = Pump()
    test_diameter = 20.5
    pump.syringe_diameter = test_diameter
    assert pump.syringe_diameter == test_diameter

    # Test invalid diameter
    with pytest.raises(ValueError):
        pump.syringe_diameter = Pump.SYRINGE_DIAMETER_MAXIMUM + 1


def test_mock_pump_pumping_direction():
    """Test pumping direction getter and setter"""
    pump = Pump()
    pump.pumping_direction = PumpingDirection.INFUSE
    assert pump.pumping_direction == PumpingDirection.INFUSE

    pump.pumping_direction = PumpingDirection.WITHDRAW
    assert pump.pumping_direction == PumpingDirection.WITHDRAW


def test_mock_pump_volume_and_rate():
    """Test volume and rate getters and setters"""
    pump = Pump()

    test_volume = 5.0
    pump.pumping_volume = test_volume
    assert pytest.approx(pump.pumping_volume) == test_volume

    test_rate = 2.5
    pump.pumping_rate = test_rate
    assert pytest.approx(pump.pumping_rate) == test_rate


def test_mock_pump_run():
    """Test run functionality"""
    pump = Pump()
    pump.syringe_diameter = 20.0
    pump.pumping_direction = PumpingDirection.INFUSE
    pump.pumping_volume = 5.0
    pump.pumping_rate = 1.0

    # Get initial volume
    initial_volume = pump.volume_infused

    # Run the pump (in mock this just updates volumes)
    pump.run()

    # The infused volume should have increased
    assert pump.volume_infused > initial_volume

    # Test volume clear
    pump.volume_infused_clear()
    assert pump.volume_infused == 0.0


def test_mock_pump_withdraw():
    """Test withdrawal functionality"""
    pump = Pump()
    pump.syringe_diameter = 20.0
    pump.pumping_direction = PumpingDirection.WITHDRAW
    pump.pumping_volume = 3.0
    pump.pumping_rate = 1.0

    # Get initial volume
    initial_volume = pump.volume_withdrawn

    # Run the pump (in mock this just updates volumes)
    pump.run()

    # The withdrawn volume should have increased
    assert pump.volume_withdrawn > initial_volume

    # Test volume clear
    pump.volume_withdrawn_clear()
    assert pump.volume_withdrawn == 0.0


def test_mock_pump_status():
    """Test the status of the mock pump"""
    pump = Pump()
    assert pump.status == Status.STOPPED
    assert not pump.running
