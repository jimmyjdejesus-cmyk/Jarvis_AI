#!/usr/bin/env python3
"""
Main entry point for Jarvis AI V2
"""

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from v2.agent.core.agent import JarvisAgentV2
from v2.config.config import DEFAULT_CONFIG

def main():
    """Initialize and run the Jarvis AI V2 system."""
    print("🚀 Starting Jarvis AI V2")
    
    # Initialize the agent
    agent = JarvisAgentV2(config=DEFAULT_CONFIG)
    
    # Set up the workflow
    agent.setup_workflow()
    
    # Example query
    result = agent.run_workflow("Help me understand LangGraph architecture")
    
    print(f"✅ Result: {result}")
    
if __name__ == "__main__":
    main()
