"""
Tools module for Jarvis AI
"""

import sys
from pathlib import Path

# Add legacy path for imports
legacy_path = Path(__file__).parent.parent / "legacy"
sys.path.insert(0, str(legacy_path))

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
