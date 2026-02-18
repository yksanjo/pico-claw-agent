"""
Example: Pico Claw with AI Agent Integration

This example demonstrates how to integrate Pico Claw with an AI agent framework.
It shows a pattern where the AI agent controls hardware through the Pico.

The architecture follows the "Thin Client" model:
- AI Agent (runs on computer/phone) handles reasoning
- Pico Claw (microcontroller) handles hardware control
- Communication via USB Serial

This example uses a mock agent to demonstrate the integration pattern.
Replace the mock with your actual AI agent framework (OpenAI, Anthropic, etc.)
"""

import json
import time
import sys
from typing import Dict, Any, List, Optional

# Add parent directory to path for pico_claw import
sys.path.insert(0, '/Users/yoshikondo/pico-claw-agent/host')

try:
    from pico_claw import PicoClaw, auto_connect
    PICO_CLAW_AVAILABLE = True
except ImportError:
    PICO_CLAW_AVAILABLE = False
    print("Warning: pico_claw library not available. Using mock.")


# ============================================================================
# MOCK AGENT (Replace with actual AI agent)
# ============================================================================

class MockAIAgent:
    """Mock AI agent for demonstration
    
    In a real implementation, replace this with:
    - OpenAI Agents SDK
    - Anthropic Claude
    - LangChain agents
    - Custom LLM integration
    """
    
    def __init__(self, claw: Optional[PicoClaw] = None):
        self.claw = claw
        self.conversation_history: List[Dict[str, str]] = []
        self.system_prompt = """You are a hardware control AI assistant.
You have access to a Raspberry Pi Pico microcontroller through which you can:
- Control GPIO pins (turn LEDs on/off, read switches)
- Control PWM (motor speed, servo position)
- Read sensors (ADC voltage, temperature)
- Communicate over I2C/SPI

Available commands:
- gpio_write(pin, value) - Write 0 or 1 to a pin
- gpio_read(pin) - Read pin value
- pwm_start(pin, frequency, duty) - Start PWM
- adc_read(channel) - Read ADC channel
- i2c_scan() - Scan for I2C devices

Always confirm actions and report sensor values."""
    
    def process_message(self, user_message: str) -> str:
        """Process a user message and generate response
        
        In a real implementation, this would call an LLM API.
        Here we simulate the pattern.
        """
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Simulate AI thinking (in reality, call LLM here)
        response = self._simulate_ai_response(user_message)
        
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        return response
    
    def _simulate_ai_response(self, user_message: str) -> str:
        """Simulate AI response - replace with actual LLM call"""
        user_lower = user_message.lower()
        
        if "led" in user_lower and "on" in user_lower:
            if self.claw:
                self.claw.gpio_write(pin=25, value=1)
            return "I've turned on the on-board LED (GPIO 25)."
        
        elif "led" in user_lower and "off" in user_lower:
            if self.claw:
                self.claw.gpio_write(pin=25, value=0)
            return "I've turned off the on-board LED."
        
        elif "read" in user_lower and ("sensor" in user_lower or "adc" in user_lower):
            if self.claw:
                voltage = self.claw.adc_read_voltage(channel=0)
                return f"ADC channel 0 voltage: {voltage:.3f}V"
            return "ADC reading: 0.000V (no hardware connected)"
        
        elif "help" in user_lower:
            return """I can help you control hardware. Try:
- "Turn the LED on" / "Turn the LED off"
- "Read the sensor on ADC channel 0"
- "Help" to see this message"""
        
        else:
            return f"I understand: '{user_message}'. How would you like to control the hardware?"


# ============================================================================
# TOOL SCHEMA (For AI Agent Frameworks)
# ============================================================================

# This schema defines the tools available to the AI agent
# Use this with OpenAI Agents, LangChain, or similar frameworks

PICO_CLAW_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "gpio_write",
            "description": "Write a digital value (0 or 1) to a GPIO pin",
            "parameters": {
                "type": "object",
                "properties": {
                    "pin": {
                        "type": "integer",
                        "description": "GPIO pin number (0-28)"
                    },
                    "value": {
                        "type": "integer",
                        "description": "Digital value: 0 (low) or 1 (high)"
                    }
                },
                "required": ["pin", "value"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "gpio_read",
            "description": "Read a digital value from a GPIO pin",
            "parameters": {
                "type": "object",
                "properties": {
                    "pin": {
                        "type": "integer",
                        "description": "GPIO pin number (0-28)"
                    }
                },
                "required": ["pin"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "pwm_start",
            "description": "Start PWM on a GPIO pin for motor/servo control",
            "parameters": {
                "type": "object",
                "properties": {
                    "pin": {
                        "type": "integer",
                        "description": "GPIO pin number"
                    },
                    "frequency": {
                        "type": "integer",
                        "description": "PWM frequency in Hz (default 1000)"
                    },
                    "duty": {
                        "type": "number",
                        "description": "Duty cycle 0.0 to 1.0 (default 0.5)"
                    }
                },
                "required": ["pin"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "adc_read_voltage",
            "description": "Read analog voltage from ADC channel",
            "parameters": {
                "type": "object",
                "properties": {
                    "channel": {
                        "type": "integer",
                        "description": "ADC channel (0-3 on RP2040, 0-7 on RP2350)"
                    }
                },
                "required": ["channel"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "i2c_scan",
            "description": "Scan I2C bus for connected devices",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]


# ============================================================================
# AGENT EXECUTION LOOP
# ============================================================================

def run_agent_loop(claw: Optional[PicoClaw] = None):
    """Run an interactive agent loop
    
    Args:
        claw: Optional PicoClaw instance
    """
    agent = MockAIAgent(claw)
    
    print("=" * 60)
    print("Pico Claw AI Agent")
    print("=" * 60)
    print("Type 'quit' to exit\n")
    
    if claw:
        print(f"Hardware connected: {claw.info.get('board')}")
        print(f"Available tools: {', '.join(claw.list_tools())}\n")
    else:
        print("Running in simulation mode (no hardware)\n")
    
    while True:
        try:
            user_input = input("You: ")
            
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            
            response = agent.process_message(user_input)
            print(f"Agent: {response}\n")
        
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}\n")


def run_automated_example(claw: Optional[PicoClaw] = None):
    """Run an automated example sequence
    
    Args:
        claw: Optional PicoClaw instance
    """
    agent = MockAIAgent(claw)
    
    print("=" * 60)
    print("Automated Example Sequence")
    print("=" * 60)
    
    test_commands = [
        "Turn the LED on",
        "Wait a moment",
        "Turn the LED off",
        "Read the sensor",
        "Help"
    ]
    
    for cmd in test_commands:
        print(f"\n>>> {cmd}")
        response = agent.process_message(cmd)
        print(f"Agent: {response}")
        time.sleep(0.5)


# ============================================================================
# LANGCHAIN INTEGRATION EXAMPLE
# ============================================================================

def langchain_example():
    """Example of LangChain integration (pseudocode)
    
    This shows how you would integrate with LangChain:
    """
    
    # from langchain_openai import ChatOpenAI
    # from langchain.agents import AgentExecutor, create_openai_functions_agent
    # from langchain.prompts import ChatPromptTemplate
    #
    # # Define tools that wrap pico_claw calls
    # tools = [
    #     # Convert pico_claw methods to LangChain tools
    # ]
    #
    # # Create prompt
    # prompt = ChatPromptTemplate.from_messages([
    #     ("system", "You are a hardware control assistant."),
    #     ("human", "{input}"),
    # ])
    #
    # # Create agent
    # llm = ChatOpenAI(model="gpt-4")
    # agent = create_openai_functions_agent(llm, tools, prompt)
    # executor = AgentExecutor(agent=agent, tools=tools)
    #
    # # Run
    # result = executor.invoke({"input": "Turn on the LED"})
    pass


# ============================================================================
# OPENAI AGENTS SDK INTEGRATION EXAMPLE
# ============================================================================

def openai_agents_example():
    """Example of OpenAI Agents SDK integration (pseudocode)
    
    This shows how you would integrate with OpenAI Agents:
    """
    
    # from openai import OpenAI
    # from agents import Agent, function_tool
    #
    # @function_tool
    # def gpio_write(pin: int, value: int) -> str:
    #     """Write to GPIO pin"""
    #     return json.dumps(claw.gpio_write(pin, value))
    #
    # @function_tool
    # def gpio_read(pin: int) -> str:
    #     """Read GPIO pin"""
    #     return json.dumps(claw.gpio_read(pin))
    #
    # @function_tool
    # def adc_read(channel: int) -> str:
    #     """Read ADC channel"""
    #     return json.dumps(claw.adc_read_voltage(channel))
    #
    # # Create agent
    # agent = Agent(
    #     name="Hardware Controller",
    #     instructions="You control a Raspberry Pi Pico microcontroller.",
    #     tools=[gpio_write, gpio_read, adc_read]
    # )
    #
    # # Run
    # result = agent.run("Turn on the LED on GPIO 25")
    pass


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Try to connect to hardware
    claw = None
    
    if PICO_CLAW_AVAILABLE:
        print("Looking for Pico Claw device...")
        claw = auto_connect()
        
        if claw:
            print(f"Connected to {claw.info.get('board')}\n")
        else:
            print("No Pico found. Running in simulation mode.\n")
    
    # Run automated example
    run_automated_example(claw)
    
    # Clean up
    if claw:
        claw.disconnect()
