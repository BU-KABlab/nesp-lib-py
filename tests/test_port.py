from unittest.mock import patch

import pytest
import serial
from nesp_lib.port import Port


def test_port_initialization(patched_serial):
    """Test that a port can be initialized with the mock serial"""
    port = Port("MOCK_PORT")
    assert port is not None


def test_port_initialization_failure():
    """Test port initialization failure cases"""
    # Test invalid baud rate
    with patch("serial.Serial", side_effect=ValueError()):
        with pytest.raises(ValueError):
            Port("MOCK_PORT", baud_rate=-1)

    # Test port unavailable
    with patch("serial.Serial", side_effect=serial.SerialException()):
        with pytest.raises(Port.Unavailability):
            Port("UNAVAILABLE_PORT")


def test_port_transmit_receive(mock_port, patched_serial):
    """Test port transmit and receive methods"""
    # Set a response
    test_data = b"test_response"
    patched_serial.set_response(test_data)

    # Transmit some data
    test_command = b"test_command"
    mock_port._transmit(test_command)

    # Check that data was written to serial
    assert test_command in patched_serial._buffer

    # Test receive
    received_data = mock_port._receive(len(test_data))
    assert received_data == test_data


def test_port_waiting_properties(mock_port, patched_serial):
    """Test the waiting properties of the port"""
    # Setup mock values
    patched_serial.in_waiting = 5
    patched_serial.out_waiting = 3

    assert mock_port._waiting_receive == 5
    assert mock_port._waiting_transmit == 3


def test_port_open_close(mock_port, patched_serial):
    """Test port open and close methods"""
    # Should be open by default
    assert patched_serial.is_open is True

    # Test close
    mock_port.close()
    assert patched_serial.is_open is False

    # Test open
    mock_port.open()
    assert patched_serial.is_open is True
