"""
Pico Claw Agent - MicroPython Firmware
AI Agent Framework for Raspberry Pi RP2040/RP2350

This firmware implements a lightweight agent interface that can:
- Receive commands from a connected computer via USB Serial
- Control GPIO, PWM, ADC, and other peripherals
- Execute pre-registered tool functions
- Send events and responses back to the host

Target: Raspberry Pi Pico, Pico 2
"""

import machine
import ujson
import uos
import sys

# ============================================================================
# CONFIGURATION
# ============================================================================

VERSION = "1.0.0"
BOARD = "RP2040" if hasattr(machine, "RP2040") else "RP2350"

# Serial configuration
BAUD_RATE = 115200
BUFFER_SIZE = 256

# Pin definitions for common peripherals
PINS = {
    "led": 25,
    "uart_tx": 0,
    "uart_rx": 1,
    "i2c_sda": 4,
    "i2c_scl": 5,
    "spi_sck": 6,
    "spi_mosi": 7,
    "spi_miso": 4,
}

# ============================================================================
# TOOL REGISTRY
# ============================================================================

class ToolRegistry:
    """Registry for callable tools/functions"""
    
    def __init__(self):
        self.tools = {}
        self._register_builtin_tools()
    
    def _register_builtin_tools(self):
        """Register built-in hardware control tools"""
        
        # GPIO Tools
        self.register("gpio_mode", self._gpio_mode)
        self.register("gpio_write", self._gpio_write)
        self.register("gpio_read", self._gpio_read)
        
        # PWM Tools
        self.register("pwm_start", self._pwm_start)
        self.register("pwm_stop", self._pwm_stop)
        self.register("pwm_duty", self._pwm_duty)
        
        # ADC Tools
        self.register("adc_read", self._adc_read)
        self.register("adc_read_voltage", self._adc_read_voltage)
        
        # I2C Tools
        self.register("i2c_scan", self._i2c_scan)
        self.register("i2c_read", self._i2c_read)
        self.register("i2c_write", self._i2c_write)
        
        # SPI Tools
        self.register("spi_read", self._spi_read)
        self.register("spi_write", self._spi_write)
        
        # System Tools
        self.register("system_info", self._system_info)
        self.register("system_reset", self._system_reset)
        self.register("get_time", self._get_time)
        
        # Delay Tool
        self.register("delay", self._delay)
    
    def register(self, name, func):
        """Register a new tool"""
        self.tools[name] = func
    
    def unregister(self, name):
        """Unregister a tool"""
        if name in self.tools:
            del self.tools[name]
    
    def call(self, name, params=None):
        """Call a registered tool"""
        if name not in self.tools:
            return {"error": f"Unknown tool: {name}"}
        
        try:
            if params is None:
                result = self.tools[name]()
            else:
                result = self.tools[name](**params)
            return {"result": result}
        except TypeError as e:
            return {"error": f"Invalid parameters: {e}"}
        except Exception as e:
            return {"error": str(e)}
    
    def list_tools(self):
        """List all registered tools"""
        return list(self.tools.keys())
    
    # =========================================================================
    # BUILT-IN TOOL IMPLEMENTATIONS
    # =========================================================================
    
    # GPIO Tools
    def _gpio_mode(self, pin, mode="output"):
        """Set GPIO pin mode"""
        p = machine.Pin(pin, machine.Pin.OUT if mode == "output" else machine.Pin.IN)
        return {"pin": pin, "mode": mode}
    
    def _gpio_write(self, pin, value):
        """Write to GPIO pin"""
        p = machine.Pin(pin, machine.Pin.OUT)
        p.value(value)
        return {"pin": pin, "value": value}
    
    def _gpio_read(self, pin):
        """Read GPIO pin"""
        p = machine.Pin(pin, machine.Pin.IN)
        return {"pin": pin, "value": p.value()}
    
    # PWM Tools
    def _pwm_start(self, pin, frequency=1000, duty=0.5):
        """Start PWM on a pin"""
        pwm = machine.PWM(machine.Pin(pin))
        pwm.freq(frequency)
        pwm.duty_u16(int(duty * 65535))
        return {"pin": pin, "frequency": frequency, "duty": duty}
    
    def _pwm_stop(self, pin):
        """Stop PWM on a pin"""
        pwm = machine.PWM(machine.Pin(pin))
        pwm.duty_u16(0)
        return {"pin": pin, "stopped": True}
    
    def _pwm_duty(self, pin, duty):
        """Set PWM duty cycle"""
        pwm = machine.PWM(machine.Pin(pin))
        pwm.duty_u16(int(duty * 65535))
        return {"pin": pin, "duty": duty}
    
    # ADC Tools
    def _adc_read(self, channel=0):
        """Read ADC channel (0-3 on RP2040)"""
        adc = machine.ADC(channel)
        return {"channel": channel, "raw": adc.read_u16()}
    
    def _adc_read_voltage(self, channel=0):
        """Read ADC voltage"""
        adc = machine.ADC(channel)
        raw = adc.read_u16()
        voltage = (raw / 65535) * 3.3
        return {"channel": channel, "voltage": round(voltage, 3)}
    
    # I2C Tools
    def _i2c_scan(self, scl=5, sda=4, frequency=400000):
        """Scan I2C bus for devices"""
        i2c = machine.I2C(0, scl=machine.Pin(scl), sda=machine.Pin(sda), freq=frequency)
        devices = i2c.scan()
        return {"devices": [hex(d) for d in devices], "count": len(devices)}
    
    def _i2c_read(self, address, register=0x00, length=1, scl=5, sda=4):
        """Read from I2C device"""
        i2c = machine.I2C(0, scl=machine.Pin(scl), sda=machine.Pin(sda))
        data = i2c.readfrom_mem(address, register, length)
        return {"address": hex(address), "data": list(data)}
    
    def _i2c_write(self, address, register=0x00, data=None, scl=5, sda=4):
        """Write to I2C device"""
        i2c = machine.I2C(0, scl=machine.Pin(scl), sda=machine.Pin(sda))
        if data:
            i2c.writeto_mem(address, register, bytes(data))
        return {"address": hex(address), "written": len(data) if data else 0}
    
    # SPI Tools
    def _spi_read(self, frequency=1000000, length=1, sck=6, mosi=7, miso=4):
        """Read from SPI"""
        spi = machine.SPI(0, baudrate=frequency, sck=machine.Pin(sck), 
                         mosi=machine.Pin(mosi), miso=machine.Pin(miso))
        data = spi.read(length)
        return {"data": list(data)}
    
    def _spi_write(self, data, frequency=1000000, sck=6, mosi=7, miso=4):
        """Write to SPI"""
        spi = machine.SPI(0, baudrate=frequency, sck=machine.Pin(sck), 
                         mosi=machine.Pin(mosi), miso=machine.Pin(miso))
        spi.write(bytes(data))
        return {"written": len(data)}
    
    # System Tools
    def _system_info(self):
        """Get system information"""
        return {
            "version": VERSION,
            "board": BOARD,
            "python_version": sys.version,
            "frequency": machine.freq(),
            "mem_free": uos.mem_free() if hasattr(uos, "mem_free") else "N/A",
        }
    
    def _system_reset(self):
        """Reset the system"""
        machine.reset()
    
    def _get_time(self):
        """Get current time (RTC if available)"""
        import time
        return {"time_ms": time.ticks_ms(), "time_us": time.ticks_us()}
    
    def _delay(self, milliseconds=0):
        """Delay for specified milliseconds"""
        import time
        time.sleep_ms(milliseconds)
        return {"delayed_ms": milliseconds}


# ============================================================================
# CONTEXT MANAGER
# ============================================================================

class ContextManager:
    """Manages conversation context and state"""
    
    def __init__(self, max_history=10):
        self.max_history = max_history
        self.history = []
        self.state = {}
    
    def add(self, role, content):
        """Add a message to history"""
        self.history.append({"role": role, "content": content})
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def get_history(self):
        """Get conversation history"""
        return self.history
    
    def clear(self):
        """Clear history"""
        self.history = []
    
    def set_state(self, key, value):
        """Set state value"""
        self.state[key] = value
    
    def get_state(self, key, default=None):
        """Get state value"""
        return self.state.get(key, default)


# ============================================================================
# AGENT ENGINE
# ============================================================================

class AgentEngine:
    """Lightweight agent execution engine"""
    
    def __init__(self):
        self.registry = ToolRegistry()
        self.context = ContextManager()
        self.running = False
        self.event_callbacks = []
    
    def execute(self, instruction):
        """Execute an instruction"""
        if isinstance(instruction, str):
            try:
                instruction = ujson.loads(instruction)
            except:
                return {"error": "Invalid JSON"}
        
        if not isinstance(instruction, dict):
            return {"error": "Invalid instruction format"}
        
        # Extract command type
        cmd = instruction.get("type", "exec")
        
        if cmd == "exec":
            tool = instruction.get("tool")
            params = instruction.get("params")
            return self.registry.call(tool, params)
        
        elif cmd == "register":
            name = instruction.get("name")
            # For custom tools, we'd need to eval/compile - simplified here
            return {"error": "Dynamic registration not implemented"}
        
        elif cmd == "list_tools":
            return {"tools": self.registry.list_tools()}
        
        elif cmd == "context":
            action = instruction.get("action", "get")
            if action == "get":
                return {"history": self.context.get_history()}
            elif action == "clear":
                self.context.clear()
                return {"cleared": True}
            elif action == "add":
                role = instruction.get("role", "user")
                content = instruction.get("content", "")
                self.context.add(role, content)
                return {"added": True}
        
        elif cmd == "state":
            key = instruction.get("key")
            action = instruction.get("action", "get")
            value = instruction.get("value")
            
            if action == "set":
                self.context.set_state(key, value)
                return {"key": key, "value": value}
            elif action == "get":
                return {"key": key, "value": self.context.get_state(key)}
        
        return {"error": f"Unknown command: {cmd}"}
    
    def on_event(self, callback):
        """Register event callback"""
        self.event_callbacks.append(callback)
    
    def emit_event(self, event_type, data):
        """Emit an event to all callbacks"""
        for callback in self.event_callbacks:
            try:
                callback(event_type, data)
            except:
                pass


# ============================================================================
# COMMUNICATION BRIDGE
# ============================================================================

class CommunicationBridge:
    """Handles serial communication with host"""
    
    def __init__(self, uart_id=0, baudrate=BAUD_RATE):
        self.uart = machine.UART(uart_id, baudrate)
        self.buffer = ""
    
    def readline(self):
        """Read a line from serial"""
        if self.uart.any():
            data = self.uart.read()
            if data:
                try:
                    self.buffer += data.decode('utf-8')
                except:
                    pass
                
                if '\n' in self.buffer:
                    lines = self.buffer.split('\n')
                    self.buffer = lines[-1]
                    return lines[0]
        return None
    
    def write(self, data):
        """Write data to serial"""
        if isinstance(data, dict):
            data = ujson.dumps(data)
        self.uart.write(data + '\n')
    
    def respond(self, status, data):
        """Send a response"""
        response = {"status": status}
        if status == "ok":
            response["data"] = data
        else:
            response["error"] = data
        self.write(response)
    
    def send_event(self, event_type, data):
        """Send an event"""
        self.write({"event": event_type, "data": data})


# ============================================================================
# MAIN APPLICATION
# ============================================================================

class PicoClawAgent:
    """Main application class"""
    
    def __init__(self):
        self.agent = AgentEngine()
        self.bridge = CommunicationBridge()
        
        # Set up LED for status
        self.led = machine.Pin(25, machine.Pin.OUT)
        self.led.off()
        
        # Register event handler
        self.agent.on_event(self._handle_event)
    
    def _handle_event(self, event_type, data):
        """Handle agent events"""
        self.bridge.send_event(event_type, data)
    
    def start(self):
        """Start the agent"""
        print("=" * 50)
        print(f"Pico Claw Agent v{VERSION}")
        print(f"Board: {BOARD}")
        print("=" * 50)
        
        self.bridge.write({
            "event": "ready",
            "data": {
                "version": VERSION,
                "board": BOARD,
                "tools": self.agent.registry.list_tools()
            }
        })
        
        self.led.on()  # LED on when ready
        self.running = True
        
        self._main_loop()
    
    def _main_loop(self):
        """Main execution loop"""
        while self.running:
            line = self.bridge.readline()
            
            if line:
                line = line.strip()
                if not line:
                    continue
                
                # Blink LED on command
                self.led.off()
                
                try:
                    result = self.agent.execute(line)
                    
                    if "error" in result:
                        self.bridge.respond("error", result["error"])
                    else:
                        self.bridge.respond("ok", result)
                
                except Exception as e:
                    self.bridge.respond("error", str(e))
                
                self.led.on()
    
    def stop(self):
        """Stop the agent"""
        self.running = False


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Entry point"""
    agent = PicoClawAgent()
    agent.start()


if __name__ == "__main__":
    main()
