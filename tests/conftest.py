from unittest.mock import MagicMock, patch

import pytest
from nesp_lib.mock import Pump as MockPump
from nesp_lib.port import Port


class MockSerial(MagicMock):
    """Mock serial connection for testing without hardware"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_open = True
        self.in_waiting = 0
        self.out_waiting = 0
        self._buffer = bytearray()
        self._response_data = bytearray()

    def write(self, data):
        """Mock write method"""
        self._buffer.extend(data)
        return len(data)

    def read(self, size=1):
        """Mock read method"""
        if not self._response_data:
            # Default response - simple STX + "00S" + ETX response (pump at address 0, stopped)
            self._response_data = bytearray([0x02, 0x05, 0x30, 0x30, 0x53, 0x03])

        if size > len(self._response_data):
            size = len(self._response_data)

        result = self._response_data[:size]
        self._response_data = self._response_data[size:]
        return bytes(result)

    def set_response(self, data):
        """Set the next response data"""
        if isinstance(data, str):
            data = data.encode()
        self._response_data = bytearray(data)
        # Uncomment for debugging only
        # print("Response data set:", " ".join(f"0x{b:02x}" for b in self._response_data))

    def close(self):
        """Mock close method"""
        self.is_open = False

    def open(self):
        """Mock open method"""
        self.is_open = True


@pytest.fixture
def mock_serial():
    """Return a mock serial object"""
    return MockSerial()


@pytest.fixture
def patched_serial(mock_serial):
    """Patch the serial.Serial to use our mock instead"""
    with patch("serial.Serial", return_value=mock_serial):
        yield mock_serial


@pytest.fixture
def mock_port(patched_serial):
    """Return a Port object with mocked Serial"""
    port = Port("MOCK_PORT")
    return port


@pytest.fixture
def mock_pump():
    """Return a mock pump object"""
    pump = MockPump()
    return pump
