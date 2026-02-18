# Pico Claw Agent

AI Agent Framework for Raspberry Pi Microcontrollers (RP2040/RP2350)

## Overview

Pico Claw adapts AI agent frameworks to run on resource-constrained Raspberry Pi microcontrollers. It follows a **Thin Client** architecture where:

- **AI Agent** (runs on computer/phone) handles reasoning and decision-making
- **Pico Claw** (microcontroller) handles hardware control
- Communication via **USB Serial** or UART

## Hardware Support

| Microcontroller | SRAM | CPU | Notes |
|---------------|------|-----|-------|
| RP2040 | 264 KB | Dual-core Cortex-M0+ @ 133 MHz | Original Pico |
| **RP2350** | 520 KB | Dual-core Cortex-M33 @ 150 MHz | Recommended - more resources |

## Project Structure

```
pico-claw-agent/
├── SPEC.md                    # Project specification
├── README.md                  # This file
├── firmware/
│   └── micropython/
│       └── main.py           # MicroPython firmware
├── host/
│   └── pico_claw.py          # Python host library
└── examples/
    └── agent_integration.py   # AI agent integration example
```

## Quick Start

### 1. Install Dependencies

```bash
# Install pyserial for serial communication
pip install pyserial

# For auto-connect feature
pip install pyserial
```

### 2. Flash Firmware to Pico

**Option A: MicroPython (Recommended)**

1. Download MicroPython UF2 from https://micropython.org/download/
2. Hold BOOTSEL button while connecting Pico to computer
3. Copy UF2 file to Pico drive
4. Copy `firmware/micropython/main.py` to Pico via Thonny or ampy

**Option B: C/C++ SDK (Advanced)**

See [Raspberry Pi Pico SDK](https://github.com/raspberrypi/pico-sdk)

### 3. Run Example

```bash
cd pico-claw-agent
python examples/agent_integration.py
```

## API Usage

### Connect to Pico

```python
from pico_claw import PicoClaw, auto_connect

# Auto-detect and connect
claw = auto_connect()

# Or manual connect
claw = PicoClaw(port="/dev/ttyUSB0")
claw.connect()
```

### Control Hardware

```python
# LED control
claw.gpio_write(pin=25, value=1)  # LED on
claw.gpio_write(pin=25, value=0)  # LED off

# PWM motor control
claw.pwm_start(pin=16, frequency=1000, duty=0.5)
claw.pwm_duty(pin=16, duty=0.75)

# Read sensors
voltage = claw.adc_read_voltage(channel=0)

# I2C devices
devices = claw.i2c_scan()
```

### Integration with AI Agents

```python
# Define tools for your AI agent framework
tools = [
    {
        "name": "gpio_write",
        "function": lambda pin, value: claw.gpio_write(pin, value)
    },
    # ... more tools
]

# Use with OpenAI Agents, LangChain, etc.
```

## Command Protocol

The firmware accepts JSON commands via serial:

```json
{"type": "exec", "tool": "gpio_write", "params": {"pin": 25, "value": 1}}
```

Response:
```json
{"status": "ok", "data": {"result": {"pin": 25, "value": 1}}}
```

## Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| gpio_mode | Set pin mode | pin, mode |
| gpio_write | Write digital value | pin, value |
| gpio_read | Read digital value | pin |
| pwm_start | Start PWM | pin, frequency, duty |
| pwm_stop | Stop PWM | pin |
| pwm_duty | Set duty cycle | pin, duty |
| adc_read | Read ADC raw | channel |
| adc_read_voltage | Read voltage | channel |
| i2c_scan | Scan I2C bus | - |
| i2c_read | Read I2C | address, register, length |
| i2c_write | Write I2C | address, register, data |
| system_info | Get system info | - |
| system_reset | Reset Pico | - |

## Development

### Running Tests

```bash
# Test without hardware
python examples/agent_integration.py
```

### Adding Custom Tools

1. Add method to `ToolRegistry` class in `firmware/micropython/main.py`
2. Register in `_register_builtin_tools()`
3. Add wrapper method in `host/pico_claw.py`

## Resources

- [Raspberry Pi Pico SDK](https://github.com/raspberrypi/pico-sdk)
- [MicroPython for RP2040](https://docs.micropython.org/en/latest/rp2.html)
- [RP2040 Datasheet](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf)
- [RP2350 Datasheet](https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf)

## License

MIT License - Feel free to use and modify for your projects.
