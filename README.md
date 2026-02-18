# 🤖 Pico Claw Agent

<p align="center">
  <img src="https://img.shields.io/badge/Microcontroller-RP2040%2FRP2350-blue?style=for-the-badge" alt="Microcontroller">
  <img src="https://img.shields.io/badge/Language-MicroPython-orange?style=for-the-badge" alt="Language">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

> **AI Agent Framework for Raspberry Pi Microcontrollers**

Pico Claw adapts AI agent frameworks to run on resource-constrained Raspberry Pi microcontrollers. It follows a **Thin Client** architecture where the AI agent handles reasoning while Pico handles hardware control.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔌 **GPIO Control** | Digital input/output on all GPIO pins |
| 🌊 **PWM Support** | Motor and servo control |
| 📊 **ADC Reading** | Analog sensor reading |
| 🔍 **I2C/SPI** | Communication with sensors and displays |
| 📡 **Serial API** | JSON-based command protocol |
| 🔗 **AI Integration** | Works with OpenAI, LangChain, Anthropic |

---

## 📐 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Agent (Your Computer)                │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐   │
│  │   Claude    │  │    GPT-4    │  │   LangChain     │   │
│  │  (Anthropic)│  │  (OpenAI)   │  │    Agents       │   │
│  └──────┬──────┘  └──────┬──────┘  └────────┬────────┘   │
│         │                  │                   │             │
│         └──────────────────┼───────────────────┘             │
│                            │                               │
│                    JSON Commands                           │
└────────────────────────────┼───────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│               Pico Claw Agent (RP2040/RP2350)              │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Firmware (MicroPython)                  │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌───────────┐  │   │
│  │  │    Tool     │  │   Agent     │  │  Context  │  │   │
│  │  │  Registry   │  │   Engine    │  │  Manager  │  │   │
│  │  └─────────────┘  └─────────────┘  └───────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│                            │                               │
│         ┌──────────────────┼──────────────────┐            │
│         ▼                  ▼                  ▼            │
│   ┌──────────┐      ┌──────────┐      ┌──────────┐    │
│   │   GPIO   │      │   PWM    │      │   ADC    │    │
│   └──────────┘      └──────────┘      └──────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔬 How It Works

```
User: "Turn on the LED"

        │
        ▼
┌───────────────────┐
│   AI Agent        │  Reasons: User wants LED on
│   (Computer)      │  Action: Call gpio_write(pin=25, value=1)
└────────┬──────────┘
         │
         │ {"type": "exec", "tool": "gpio_write", "params": {"pin": 25, "value": 1}}
         ▼
┌───────────────────┐
│  Pico Claw       │  Receives command via USB Serial
│  (Microcontroller)│  Executes: machine.Pin(25).value(1)
└────────┬──────────┘
         │
         │ {"status": "ok", "data": {"result": {"pin": 25, "value": 1}}}
         ▼
┌───────────────────┐
│   AI Agent        │  Responds to user
│   (Computer)      │  "LED is now on!"
└───────────────────┘
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install pyserial
```

### 2. Flash Firmware to Pico

**Option A: MicroPython (Recommended)**

1. Download MicroPython UF2 from [micropython.org](https://micropython.org/download/)
2. Hold **BOOTSEL** button while connecting Pico to computer
3. Copy UF2 file to the **RPI-RP2** drive
4. Copy `firmware/micropython/main.py` to Pico using Thonny:

<p align="center">
  <img src="docs/images/thonny-screenshot.png" alt="Thonny IDE" width="600">
</p>

**Option B: C/C++ SDK (Advanced)**

See [Raspberry Pi Pico SDK](https://github.com/raspberrypi/pico-sdk)

### 3. Run Example

```bash
python examples/agent_integration.py
```

**Expected Output:**
```
============================================================
Automated Example Sequence
============================================================

>>> Turn the LED on
Agent: I've turned on the on-board LED (GPIO 25).

>>> Wait a moment
Agent: I've waited for 100ms.

>>> Turn the LED off
Agent: I've turned off the on-board LED.

>>> Read the sensor
Agent: ADC channel 0 voltage: 0.123V

>>> Help
Agent: I can help you control hardware. Try:
- "Turn the LED on" / "Turn the LED off"
- "Read the sensor on ADC channel 0"
- "Help" to see this message
```

---

## 💻 API Usage

### Connect to Pico

```python
from pico_claw import PicoClaw, auto_connect

# Auto-detect and connect
claw = auto_connect()

# Or manual connect
claw = PicoClaw(port="/dev/ttyUSB0")
claw.connect()

print(f"Connected to {claw.info['board']}")
print(f"Available tools: {claw.list_tools()}")
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
        "description": "Write to GPIO pin (0=off, 1=on)",
        "parameters": {
            "type": "object",
            "properties": {
                "pin": {"type": "integer", "description": "GPIO pin 0-28"},
                "value": {"type": "integer", "description": "0 or 1"}
            },
            "required": ["pin", "value"]
        }
    },
    {
        "name": "adc_read_voltage",
        "description": "Read analog voltage",
        "parameters": {
            "type": "object", 
            "properties": {
                "channel": {"type": "integer", "description": "ADC channel 0-3"}
            },
            "required": ["channel"]
        }
    }
]

# Use with OpenAI Agents, LangChain, Anthropic, etc.
```

---

## 🔧 Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `gpio_mode` | Set pin mode | `pin`, `mode` |
| `gpio_write` | Write digital value | `pin`, `value` |
| `gpio_read` | Read digital value | `pin` |
| `pwm_start` | Start PWM | `pin`, `frequency`, `duty` |
| `pwm_stop` | Stop PWM | `pin` |
| `pwm_duty` | Set duty cycle | `pin`, `duty` |
| `adc_read` | Read ADC raw | `channel` |
| `adc_read_voltage` | Read voltage | `channel` |
| `i2c_scan` | Scan I2C bus | - |
| `i2c_read` | Read I2C | `address`, `register`, `length` |
| `i2c_write` | Write I2C | `address`, `register`, `data` |
| `system_info` | Get system info | - |
| `system_reset` | Reset Pico | - |

---

## 🛠️ Hardware Support

| Microcontroller | SRAM | CPU | Notes |
|----------------|------|-----|-------|
| RP2040 | 264 KB | Dual-core Cortex-M0+ @ 133 MHz | Original Pico |
| **RP2350** | 520 KB | Dual-core Cortex-M33 @ 150 MHz | ⭐ Recommended |

---

## 📁 Project Structure

```
pico-claw-agent/
├── 📄 SPEC.md                     # Project specification
├── 📄 README.md                   # This file
├── 📁 docs/
│   └── 📁 images/                # Screenshots
├── 📁 firmware/
│   └── 📁 micropython/
│       └── 📄 main.py             # MicroPython firmware
├── 📁 host/
│   └── 📄 pico_claw.py           # Python host library
└── 📁 examples/
    └── 📄 agent_integration.py    # AI agent integration
```

---

## 🔗 Resources

- 📘 [Raspberry Pi Pico SDK](https://github.com/raspberrypi/pico-sdk)
- 🐍 [MicroPython for RP2040](https://docs.micropython.org/en/latest/rp2.html)
- 📊 [RP2040 Datasheet](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf)
- 📊 [RP2350 Datasheet](https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf)

---

## 📄 License

MIT License - Feel free to use and modify!

---

<p align="center">
  Made with ❤️ for AI Agents + Hardware
</p>
