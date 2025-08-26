"""
Core agent functionality for Jarvis AI
"""

import sys
from pathlib import Path


try:
    from agent.core.core import JarvisAgent
except ImportError:
    # Fallback implementation
    class JarvisAgent:
        def __init__(self, model_name="llama3.2"):
            self.model_name = model_name
        
        def chat(self, message):
            return f"Echo: {message} (using {self.model_name})"
