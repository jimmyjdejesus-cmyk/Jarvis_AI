# MCP (Model Context Protocol) Package
"""
Model Context Protocol implementation for Jarvis AI

This package provides:
- MCPClient: Core client for MCP communication
- MCPServerManager: Management of multiple MCP servers  
- ModelRouter: Intelligent routing to best models
"""

from .client import MCPClient
from .server_manager import MCPServerManager
from .model_router import ModelRouter

__all__ = ['MCPClient', 'MCPServerManager', 'ModelRouter']

# Version info
__version__ = "1.0.0"
__author__ = "Jarvis AI Team"
