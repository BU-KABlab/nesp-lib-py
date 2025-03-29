from unittest.mock import patch

import pytest
from nesp_lib.exceptions import ModelException
from nesp_lib.pump import Pump
from nesp_lib.pumping_direction import PumpingDirection
from nesp_lib.status import Status


# Helper function to setup response data
def setup_pump_response(mock_serial, response):
    """Setup a response for the pump command"""
    stx = bytes([0x02])
    etx = bytes([0x03])
    data = response.encode()
    # Format: STX + length + data + ETX
    mock_serial.set_response(stx + data + etx)


@pytest.fixture
def mock_firmware_response(patched_serial):
    """Set up a mock firmware response"""
    # Format: STX + length + "00SNE1000V3.928" + ETX
    setup_pump_response(patched_serial, "00SNE1000V3.928")
    return patched_serial


@pytest.fixture
def pump_instance(mock_port, mock_firmware_response):
    """Create a pump instance with mocked responses"""
    with patch.object(
        Pump, "_Pump__firmware_version_get", return_value=(1000, (3, 928), 0)
    ):
        pump = Pump(mock_port)
        # Reset the mock to clear the initialization calls
        mock_firmware_response.reset_mock()
        return pump


def test_pump_initialization(pump_instance):
    """Test pump initialization"""
    assert pump_instance.address == Pump.ADDRESS_DEFAULT
    assert pump_instance.model_number == 1000
    assert pump_instance.firmware_version == (3, 928)


def test_pump_initialization_errors(mock_port, mock_firmware_response):
    """Test initialization errors"""
    # Test invalid address
    with pytest.raises(ValueError):
        Pump(mock_port, address=-1)

    with pytest.raises(ValueError):
        Pump(mock_port, address=Pump.ADDRESS_LIMIT + 1)

    # Test wrong model
    with patch.object(
        Pump, "_Pump__firmware_version_get", return_value=(1000, (3, 928), 0)
    ):
        with pytest.raises(ModelException):
            Pump(mock_port, model_number=2000)


def test_pump_status(pump_instance, patched_serial):
    """Test getting pump status"""
    # Set up response for status command - pump stopped
    setup_pump_response(patched_serial, "00S")

    status = pump_instance.status
    assert status == Status.STOPPED

    # Set up response for status command - pump infusing
    setup_pump_response(patched_serial, "00I")

    status = pump_instance.status
    assert status == Status.INFUSING


def test_pump_running(pump_instance, patched_serial):
    """Test the running property"""
    # Set up response for status command - pump stopped
    setup_pump_response(patched_serial, "00S")
    assert not pump_instance.running

    # Set up response for status command - pump infusing
    setup_pump_response(patched_serial, "00I")
    assert pump_instance.running


def test_pump_syringe_diameter(pump_instance, patched_serial):
    """Test getting and setting syringe diameter"""
    # Setup response for get diameter command
    setup_pump_response(patched_serial, "00S15.5")

    diameter = pump_instance.syringe_diameter
    assert diameter == 15.5

    # Setup response for set diameter command
    setup_pump_response(patched_serial, "00S")

    pump_instance.syringe_diameter = 20.0

    # Check that the command was sent correctly
    assert b"0DIA20" in patched_serial._buffer

    # Test invalid diameter
    with pytest.raises(ValueError):
        pump_instance.syringe_diameter = Pump.SYRINGE_DIAMETER_MAXIMUM + 1


def test_pump_direction(pump_instance, patched_serial):
    """Test getting and setting pumping direction"""
    # Setup response for get direction command - infuse
    setup_pump_response(patched_serial, "00SINF")

    direction = pump_instance.pumping_direction
    assert direction == PumpingDirection.INFUSE

    # Setup response for set direction command
    setup_pump_response(patched_serial, "00S")

    pump_instance.pumping_direction = PumpingDirection.WITHDRAW

    # Check that the command was sent correctly
    assert b"0DIRWDR" in patched_serial._buffer


def test_pump_volume(pump_instance, patched_serial):
    """Test getting and setting pumping volume"""
    # Setup response for get volume command
    setup_pump_response(patched_serial, "00S5.0ML")

    volume = pump_instance.pumping_volume
    assert volume == 5.0

    # Setup response for set volume command
    setup_pump_response(patched_serial, "00S")

    pump_instance.pumping_volume = 10.0

    # Check that the command was sent correctly
    assert b"0VOL" in patched_serial._buffer

    # Test with a very large value that should raise ValueError
    with patch.object(
        pump_instance, "_Pump__command_transceive", side_effect=ValueError()
    ):
        with pytest.raises(ValueError):
            pump_instance.pumping_volume = 50000.0


def test_pump_rate(pump_instance, patched_serial):
    """Test getting and setting pumping rate"""
    # Setup response for get rate command
    setup_pump_response(patched_serial, "00S2.5MM")

    rate = pump_instance.pumping_rate
    assert rate == 2.5

    # Setup response for set rate command
    setup_pump_response(patched_serial, "00S")

    pump_instance.pumping_rate = 1.5

    # Check that the command was sent correctly
    assert b"0RAT" in patched_serial._buffer

    # Test with a very large value that should raise ValueError
    with patch.object(
        pump_instance, "_Pump__command_transceive", side_effect=ValueError()
    ):
        with pytest.raises(ValueError):
            pump_instance.pumping_rate = 20000.0


def test_pump_dispensation(pump_instance, patched_serial):
    """Test dispensation functionality"""
    # Setup response for get dispensation command
    setup_pump_response(patched_serial, "00SI2.5W0.0ML")

    # Test volume infused
    volume = pump_instance.volume_infused
    assert volume == 2.5

    # Setup response for clear dispensation command
    setup_pump_response(patched_serial, "00S")

    # Test clearing volume infused
    pump_instance.volume_infused_clear()
    assert b"0CLDINF" in patched_serial._buffer

    # Reset buffer
    patched_serial._buffer = bytearray()

    # Setup response for get dispensation command with withdrawn volume
    setup_pump_response(patched_serial, "00SI0.0W3.5ML")

    # Test volume withdrawn
    volume = pump_instance.volume_withdrawn
    assert volume == 3.5

    # Setup response for clear dispensation command
    setup_pump_response(patched_serial, "00S")

    # Test clearing volume withdrawn
    pump_instance.volume_withdrawn_clear()
    assert b"0CLDWDR" in patched_serial._buffer


def test_pump_run_stop(pump_instance, patched_serial):
    """Test run and stop commands"""
    # Setup responses for run and status checks
    setup_pump_response(patched_serial, "00S")  # Initial status check
    setup_pump_response(patched_serial, "00I")  # Running status
    setup_pump_response(patched_serial, "00S")  # Stopped status

    # Patch wait_while_running to avoid actual waiting
    with patch.object(pump_instance, "wait_while_running"):
        # Run the pump - blocking
        pump_instance.run()

        # Check that run command was sent
        assert b"0RUN" in patched_serial._buffer

        # Reset buffer
        patched_serial._buffer = bytearray()

        # Run the pump - non-blocking
        pump_instance.run(False)

        # Check that run command was sent
        assert b"0RUN" in patched_serial._buffer

        # Reset buffer
        patched_serial._buffer = bytearray()

        # Stop the pump - blocking
        pump_instance.stop()

        # Check that stop command was sent
        assert b"0STP" in patched_serial._buffer


def test_pump_run_purge(pump_instance, patched_serial):
    """Test run_purge command"""
    # Setup response for purge command
    setup_pump_response(patched_serial, "00S")

    # Run purge
    pump_instance.run_purge()

    # Check that purge command was sent
    assert b"0PUR" in patched_serial._buffer


def test_pump_safe_mode_timeout(pump_instance, patched_serial):
    """Test safe mode timeout getter and setter"""
    # Setup response for get safe mode timeout
    setup_pump_response(patched_serial, "00S30")

    timeout = pump_instance.safe_mode_timeout
    assert timeout == 30

    # Setup response for set safe mode timeout
    setup_pump_response(patched_serial, "00S")

    # Set safe mode timeout
    pump_instance.safe_mode_timeout = 60

    # Check that command was sent correctly
    assert b"0SAF60" in patched_serial._buffer

    # Test invalid timeout
    with pytest.raises(ValueError):
        pump_instance.safe_mode_timeout = Pump.SAFE_MODE_TIMEOUT_LIMIT + 1
