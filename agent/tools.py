"""
Tools module for Jarvis AI
"""

from pathlib import Path

try:
    import agent.tools as tools
    # Re-export tools
    __all__ = ['tools']
except ImportError:
    # Fallback implementation
    class Tools:
        def __init__(self):
            pass
        
        def get_available_tools(self):
            return ["echo", "file_reader", "web_search"]
    
    tools = Tools()
