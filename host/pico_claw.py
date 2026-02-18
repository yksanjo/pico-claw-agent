"""
Pico Claw Host Library
Python library for communicating with Pico Claw Agent firmware

This library provides a high-level interface for AI agent frameworks
to control Raspberry Pi Pico microcontrollers via serial communication.

Usage:
    from pico_claw import PicoClaw
    
    claw = PicoClaw(port="/dev/ttyUSB0")
    claw.connect()
    
    # Control GPIO
    claw.gpio_write(pin=25, value=1)
    
    # Read sensors
    voltage = claw.adc_read_voltage(channel=0)
    
    # Execute custom commands
    result = claw.execute({"type": "exec", "tool": "pwm_start", "params": {...}})
"""

import serial
import json
import time
from typing import Any, Dict, List, Optional, Union


class PicoClaw:
    """Client for Pico Claw Agent"""
    
    def __init__(
        self,
        port: str = "/dev/ttyUSB0",
        baudrate: int = 115200,
        timeout: float = 5.0,
        retry_count: int = 3
    ):
        """Initialize Pico Claw client
        
        Args:
            port: Serial port path (e.g., /dev/ttyUSB0, COM3)
            baudrate: Communication speed (default 115200)
            timeout: Read timeout in seconds
            retry_count: Number of retries for failed commands
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.retry_count = retry_count
        self.serial: Optional[serial.Serial] = None
        self.connected = False
        self.info: Dict[str, Any] = {}
    
    def connect(self) -> bool:
        """Connect to Pico Claw Agent
        
        Returns:
            True if connected successfully
        """
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                write_timeout=1.0
            )
            
            # Wait for ready event
            start_time = time.time()
            while time.time() - start_time < self.timeout:
                line = self._read_line()
                if line:
                    try:
                        msg = json.loads(line)
                        if msg.get("event") == "ready":
                            self.info = msg.get("data", {})
                            self.connected = True
                            return True
                    except json.JSONDecodeError:
                        pass
            
            return False
        
        except serial.SerialException as e:
            raise ConnectionError(f"Failed to connect to {self.port}: {e}")
    
    def disconnect(self):
        """Disconnect from Pico Claw Agent"""
        if self.serial:
            self.serial.close()
            self.serial = None
        self.connected = False
    
    def _read_line(self) -> Optional[str]:
        """Read a line from serial"""
        if not self.serial:
            return None
        
        try:
            if self.serial.in_waiting > 0:
                line = self.serial.readline()
                return line.decode('utf-8').strip()
        except:
            pass
        return None
    
    def _send_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Send command and wait for response
        
        Args:
            command: Command dictionary
            
        Returns:
            Response dictionary
        """
        if not self.connected:
            raise ConnectionError("Not connected to Pico Claw Agent")
        
        # Send command
        cmd_str = json.dumps(command) + "\n"
        self.serial.write(cmd_str.encode('utf-8'))
        
        # Wait for response
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            line = self._read_line()
            if line:
                try:
                    return json.loads(line)
                except json.JSONDecodeError:
                    pass
        
        return {"status": "error", "error": "Timeout"}
    
    def execute(self, command: Union[str, Dict]) -> Dict[str, Any]:
        """Execute a general command
        
        Args:
            command: Command as dict or JSON string
            
        Returns:
            Result dictionary
        """
        for _ in range(self.retry_count):
            if isinstance(command, str):
                try:
                    command = json.loads(command)
                except json.JSONDecodeError:
                    return {"status": "error", "error": "Invalid JSON"}
            
            result = self._send_command(command)
            if result.get("status") != "error" or "Timeout" not in result.get("error", ""):
                return result
        
        return result
    
    # =========================================================================
    # GPIO Methods
    # =========================================================================
    
    def gpio_mode(self, pin: int, mode: str = "output") -> Dict[str, Any]:
        """Set GPIO pin mode
        
        Args:
            pin: GPIO pin number
            mode: "input" or "output"
            
        Returns:
            Result with pin and mode
        """
        return self.execute({
            "type": "exec",
            "tool": "gpio_mode",
            "params": {"pin": pin, "mode": mode}
        })
    
    def gpio_write(self, pin: int, value: int) -> Dict[str, Any]:
        """Write to GPIO pin
        
        Args:
            pin: GPIO pin number
            value: 0 or 1
            
        Returns:
            Result with pin and value
        """
        return self.execute({
            "type": "exec",
            "tool": "gpio_write",
            "params": {"pin": pin, "value": value}
        })
    
    def gpio_read(self, pin: int) -> Dict[str, Any]:
        """Read GPIO pin
        
        Args:
            pin: GPIO pin number
            
        Returns:
            Result with pin value
        """
        return self.execute({
            "type": "exec",
            "tool": "gpio_read",
            "params": {"pin": pin}
        })
    
    # =========================================================================
    # PWM Methods
    # =========================================================================
    
    def pwm_start(
        self,
        pin: int,
        frequency: int = 1000,
        duty: float = 0.5
    ) -> Dict[str, Any]:
        """Start PWM on a pin
        
        Args:
            pin: GPIO pin number
            frequency: PWM frequency in Hz
            duty: Duty cycle (0.0 to 1.0)
            
        Returns:
            Result with pin, frequency, duty
        """
        return self.execute({
            "type": "exec",
            "tool": "pwm_start",
            "params": {"pin": pin, "frequency": frequency, "duty": duty}
        })
    
    def pwm_stop(self, pin: int) -> Dict[str, Any]:
        """Stop PWM on a pin
        
        Args:
            pin: GPIO pin number
            
        Returns:
            Result with stopped status
        """
        return self.execute({
            "type": "exec",
            "tool": "pwm_stop",
            "params": {"pin": pin}
        })
    
    def pwm_duty(self, pin: int, duty: float) -> Dict[str, Any]:
        """Set PWM duty cycle
        
        Args:
            pin: GPIO pin number
            duty: Duty cycle (0.0 to 1.0)
            
        Returns:
            Result with pin and duty
        """
        return self.execute({
            "type": "exec",
            "tool": "pwm_duty",
            "params": {"pin": pin, "duty": duty}
        })
    
    # =========================================================================
    # ADC Methods
    # =========================================================================
    
    def adc_read(self, channel: int = 0) -> Dict[str, Any]:
        """Read ADC channel (raw 16-bit value)
        
        Args:
            channel: ADC channel (0-3 on RP2040)
            
        Returns:
            Result with raw value
        """
        return self.execute({
            "type": "exec",
            "tool": "adc_read",
            "params": {"channel": channel}
        })
    
    def adc_read_voltage(self, channel: int = 0) -> float:
        """Read ADC voltage
        
        Args:
            channel: ADC channel
            
        Returns:
            Voltage in volts
        """
        result = self.execute({
            "type": "exec",
            "tool": "adc_read_voltage",
            "params": {"channel": channel}
        })
        
        if result.get("status") == "ok":
            data = result.get("data", {})
            return data.get("result", {}).get("voltage", 0.0)
        return 0.0
    
    # =========================================================================
    # I2C Methods
    # =========================================================================
    
    def i2c_scan(
        self,
        scl: int = 5,
        sda: int = 4,
        frequency: int = 400000
    ) -> List[int]:
        """Scan I2C bus for devices
        
        Args:
            scl: SCL pin number
            sda: SDA pin number
            frequency: I2C frequency
            
        Returns:
            List of device addresses
        """
        result = self.execute({
            "type": "exec",
            "tool": "i2c_scan",
            "params": {"scl": scl, "sda": sda, "frequency": frequency}
        })
        
        if result.get("status") == "ok":
            data = result.get("data", {})
            return data.get("result", {}).get("devices", [])
        return []
    
    def i2c_read(
        self,
        address: int,
        register: int = 0x00,
        length: int = 1,
        scl: int = 5,
        sda: int = 4
    ) -> bytes:
        """Read from I2C device
        
        Args:
            address: I2C device address
            register: Register address
            length: Number of bytes to read
            scl: SCL pin number
            sda: SDA pin number
            
        Returns:
            Data bytes
        """
        result = self.execute({
            "type": "exec",
            "tool": "i2c_read",
            "params": {
                "address": address,
                "register": register,
                "length": length,
                "scl": scl,
                "sda": sda
            }
        })
        
        if result.get("status") == "ok":
            data = result.get("data", {})
            return bytes(data.get("result", {}).get("data", []))
        return b""
    
    def i2c_write(
        self,
        address: int,
        data: Union[List[int], bytes],
        register: int = 0x00,
        scl: int = 5,
        sda: int = 4
    ) -> int:
        """Write to I2C device
        
        Args:
            address: I2C device address
            data: Data to write
            register: Register address
            scl: SCL pin number
            sda: SDA pin number
            
        Returns:
            Number of bytes written
        """
        if isinstance(data, bytes):
            data = list(data)
        
        result = self.execute({
            "type": "exec",
            "tool": "i2c_write",
            "params": {
                "address": address,
                "register": register,
                "data": data,
                "scl": scl,
                "sda": sda
            }
        })
        
        if result.get("status") == "ok":
            data = result.get("data", {})
            return data.get("result", {}).get("written", 0)
        return 0
    
    # =========================================================================
    # System Methods
    # =========================================================================
    
    def system_info(self) -> Dict[str, Any]:
        """Get system information
        
        Returns:
            System info dictionary
        """
        result = self.execute({
            "type": "exec",
            "tool": "system_info",
            "params": {}
        })
        
        if result.get("status") == "ok":
            return result.get("data", {}).get("result", {})
        return {}
    
    def system_reset(self) -> Dict[str, Any]:
        """Reset the Pico
        
        Returns:
            Result (will timeout as device resets)
        """
        return self.execute({
            "type": "exec",
            "tool": "system_reset",
            "params": {}
        })
    
    def get_time(self) -> Dict[str, Any]:
        """Get current time
        
        Returns:
            Time dictionary with ms and us
        """
        return self.execute({
            "type": "exec",
            "tool": "get_time",
            "params": {}
        })
    
    def delay(self, milliseconds: int) -> Dict[str, Any]:
        """Delay for specified milliseconds
        
        Args:
            milliseconds: Delay time
            
        Returns:
            Result with delayed_ms
        """
        return self.execute({
            "type": "exec",
            "tool": "delay",
            "params": {"milliseconds": milliseconds}
        })
    
    # =========================================================================
    # Context Methods
    # =========================================================================
    
    def list_tools(self) -> List[str]:
        """List all available tools
        
        Returns:
            List of tool names
        """
        result = self.execute({
            "type": "list_tools"
        })
        
        if result.get("status") == "ok":
            return result.get("data", {}).get("tools", [])
        return []
    
    def context_get(self) -> List[Dict[str, str]]:
        """Get conversation context
        
        Returns:
            List of context messages
        """
        result = self.execute({
            "type": "context",
            "action": "get"
        })
        
        if result.get("status") == "ok":
            return result.get("data", {}).get("history", [])
        return []
    
    def context_add(self, role: str, content: str) -> Dict[str, Any]:
        """Add to conversation context
        
        Args:
            role: Role (user, assistant, system)
            content: Message content
            
        Returns:
            Result with added status
        """
        return self.execute({
            "type": "context",
            "action": "add",
            "role": role,
            "content": content
        })
    
    def context_clear(self) -> Dict[str, Any]:
        """Clear conversation context
        
        Returns:
            Result with cleared status
        """
        return self.execute({
            "type": "context",
            "action": "clear"
        })
    
    # =========================================================================
    # State Methods
    # =========================================================================
    
    def state_get(self, key: str) -> Any:
        """Get state value
        
        Args:
            key: State key
            
        Returns:
            State value
        """
        result = self.execute({
            "type": "state",
            "action": "get",
            "key": key
        })
        
        if result.get("status") == "ok":
            return result.get("data", {}).get("value")
        return None
    
    def state_set(self, key: str, value: Any) -> Dict[str, Any]:
        """Set state value
        
        Args:
            key: State key
            value: State value
            
        Returns:
            Result with key and value
        """
        return self.execute({
            "type": "state",
            "action": "set",
            "key": key,
            "value": value
        })


# ============================================================================
# Convenience Functions
# ============================================================================

def auto_connect(baudrate: int = 115200) -> Optional[PicoClaw]:
    """Auto-detect and connect to Pico Claw
    
    Args:
        baudrate: Communication speed
        
    Returns:
        PicoClaw instance or None if not found
    """
    import serial.tools.list_ports
    
    ports = list(serial.tools.list_ports.comports())
    
    for port in ports:
        # Try common Pico port identifiers
        if "USB" in port.device or "ACM" in port.device or "SLAB" in port.device:
            try:
                claw = PicoClaw(port=port.device, baudrate=baudrate)
                if claw.connect():
                    return claw
                claw.disconnect()
            except:
                pass
    
    return None


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Example: Connect to Pico and control LED
    import sys
    
    # Try auto-connect first
    claw = auto_connect()
    
    if claw:
        print(f"Connected to Pico Claw v{claw.info.get('version')}")
        print(f"Board: {claw.info.get('board')}")
        print(f"Tools: {', '.join(claw.list_tools())}")
        
        # Blink LED
        print("\nBlinking LED...")
        claw.gpio_write(pin=25, value=1)
        time.sleep(0.5)
        claw.gpio_write(pin=25, value=0)
        
        # Read ADC
        print("\nReading ADC channel 0...")
        voltage = claw.adc_read_voltage(channel=0)
        print(f"Voltage: {voltage}V")
        
        claw.disconnect()
        print("\nDisconnected.")
    else:
        print("Pico Claw not found. Make sure it's connected via USB.")
        sys.exit(1)
