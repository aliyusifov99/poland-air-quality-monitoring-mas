"""
Base Agent Class

This is the parent class for all agents in the Multi-Agent System.
It provides common functionality like logging and message passing.
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from abc import ABC, abstractmethod
from datetime import datetime


class Message:
    """
    Message class for communication between agents.
    
    When agents talk to each other, they send Message objects containing:
    - sender: Who sent it
    - data: The actual content
    - status: success or error
    """
    
    def __init__(self, sender, data, status="success"):
        self.sender = sender
        self.data = data
        self.status = status
        self.timestamp = datetime.now()
    
    def __repr__(self):
        return f"Message(from={self.sender}, status={self.status})"


class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    
    Every agent must implement:
    - get_name(): Return the agent's name
    - process(): Main processing logic
    """
    
    def __init__(self):
        self.name = self.get_name()
    
    @abstractmethod
    def get_name(self):
        """Return the name of this agent."""
        pass
    
    @abstractmethod
    def process(self, input_message=None):
        """
        Main processing method - must be implemented by child classes.
        
        Args:
            input_message: Optional input from another agent
            
        Returns:
            Message containing the results
        """
        pass
    
    def create_message(self, data, status="success"):
        """
        Create a message to send to another agent.
        
        Args:
            data: The content to send
            status: "success" or "error"
            
        Returns:
            Message object
        """
        return Message(sender=self.name, data=data, status=status)
    
    def log(self, message):
        """Print a log message with agent name and timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {self.name}: {message}")
    
    def run(self, input_message=None):
        """
        Execute the agent with logging.
        
        This is the main entry point for running an agent.
        """
        self.log("Starting...")
        start_time = datetime.now()
        
        try:
            result = self.process(input_message)
            duration = (datetime.now() - start_time).total_seconds()
            self.log(f"Completed in {duration:.2f} seconds")
            return result
        except Exception as e:
            self.log(f"ERROR: {str(e)}")
            return self.create_message(data=None, status="error")
