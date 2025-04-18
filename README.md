# NESP-Lib – New Era Syringe Pump Library for Python

This project aims to offer a clean high-level interface to the New Era syringe pumps by New Era Pump
Systems.

These pumps are also distributed under different names, like Aladdin by World Precision Instruments
(WPI) and LA by Landgraf Laborsysteme.

This is a fork from florian-lapp's original combined with modifications from AbeKh (https://github.com/AbeKh/nesp-lib-py.git), modified to accommodate other NE models and paramaters, and add QOL features.

## Features

- Object-oriented design
- Documented public elements via type hints and docstrings
- Signaling errors via exceptions
- Blocking and non-blocking running
- Sending heartbeat messages automatically

## Installing

### From GitHub

```bash
# Install the package directly from GitHub
pip install git+https://github.com/BU-KABlab/nesp-lib-py.git

# Install with development dependencies
pip install "git+https://github.com/BU-KABlab/nesp-lib-py.git#egg=NESP-Lib[dev]"
```

### From PyPI

```bash
# Install the package
pip install NESP-Lib

# Install with development dependencies
pip install NESP-Lib[dev]
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/BU-KABlab/nesp-lib-py.git
cd nesp-lib-py

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run tests using pytest
pytest

# Run with coverage report
coverage run -m pytest
coverage report
```

## Importing

```python
import nesp_lib
```

## Examples

### Configuring

```python
from nesp_lib import Port, Pump, PumpingDirection

# Constructs the port to which the pump is connected.
port = Port('COM1')
# Constructs the pump connected to the port.
pump = Pump(port)
# Sets the syringe diameter of the pump in units of millimeters.
pump.syringe_diameter = 30.0
# Sets the pumping direction of the pump.
pump.pumping_direction = PumpingDirection.INFUSE
# Sets the pumping volume of the pump in units of milliliters.
pump.pumping_volume = 1.0
# Sets the pumping rate of the pump in units of milliliters per minute.
pump.pumping_rate = 20.0
```

### Identifying

```python
# Prints the model number of the pump (e.g. "1000" for NE-1000).
print(pump.model_number)
# Prints the firmware version of the pump (e.g. "(3, 928)" for 3.928).
print(pump.firmware_version)
```

### Running (Blocking)

Blocking running waits while the pump is running.

```python
# Runs the pump considering the direction, volume, and rate set.
pump.run()
```

### Running (Non-blocking)

Non-blocking running returns immediately after starting the running.

```python
# Starts running the pump considering the direction, volume, and rate set.
pump.run(False)
# Waits while the pump is running.
pump.wait_while_running()
# Starts running the pump considering the direction, volume, and rate set.
pump.run(False)
# Waits while the pump is running.
while pump.running :
    ...
# Starts running the pump considering the direction, volume, and rate set.
pump.run(False)
...
# Stops the pump.
pump.stop()
```
