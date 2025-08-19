#!/usr/bin/env python3
"""
Launcher script for Jarvis AI V2 Backend

This script starts the LangGraph-based backend API service.
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from agent.core.langgraph_backend import run_server
    from agent.core.config_manager import get_config
except ImportError as e:
    print(f"Error importing V2 modules: {e}")
    print("Make sure all dependencies are installed:")
    print("pip install -r requirements_enhanced.txt")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Start Jarvis AI V2 Backend")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8001, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument("--config", help="Path to configuration file")
    
    args = parser.parse_args()
    
    # Load configuration
    try:
        config = get_config()
        v2_config = config.v2
        
        if not v2_config.enabled:
            print("V2 backend is disabled in configuration")
            sys.exit(1)
        
        print(f"Starting Jarvis AI V2 Backend")
        print(f"Expert Model: {v2_config.expert_model}")
        print(f"Max Iterations: {v2_config.max_iterations}")
        print(f"LangChain Tools: {'Enabled' if v2_config.use_langchain_tools else 'Disabled'}")
        
    except Exception as e:
        print(f"Error loading configuration: {e}")
        print("Using default settings")
    
    # Start the server
    run_server(
        host=args.host,
        port=args.port,
        reload=args.reload
    )


if __name__ == "__main__":
    main()