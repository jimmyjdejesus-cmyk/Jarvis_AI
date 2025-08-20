"""
MCP Client for Model Context Protocol communication
"""
import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
import aiohttp
import requests

logger = logging.getLogger(__name__)

class MCPClient:
    """Model Context Protocol client for multi-model communication"""
    
    def __init__(self, servers: Dict[str, str] = None):
        """
        Initialize MCP client with server configurations
        
        Args:
            servers: Dictionary mapping server names to their URLs
        """
        self.servers = servers or {
            "ollama": "http://localhost:11434",
            "openai": "https://api.openai.com/v1", 
            "anthropic": "https://api.anthropic.com/v1"
        }
        self.active_connections = {}
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def connect_to_server(self, server_name: str) -> bool:
        """
        Establish connection to MCP server
        
        Args:
            server_name: Name of the server to connect to
            
        Returns:
            bool: True if connection successful
        """
        if server_name not in self.servers:
            logger.error(f"Unknown server: {server_name}")
            return False
            
        server_url = self.servers[server_name]
        
        try:
            if server_name == "ollama":
                # Test Ollama connection
                response = requests.get(f"{server_url}/api/tags", timeout=5)
                if response.status_code == 200:
                    self.active_connections[server_name] = server_url
                    logger.info(f"Connected to {server_name}")
                    return True
            else:
                # For other servers, we'll implement proper MCP handshake later
                # For now, just mark as connected
                self.active_connections[server_name] = server_url
                logger.info(f"Connected to {server_name} (basic)")
                return True
                
        except Exception as e:
            logger.error(f"Failed to connect to {server_name}: {e}")
            return False
        
        return False
    
    async def list_models(self, server_name: str) -> List[str]:
        """
        Get available models from server
        
        Args:
            server_name: Name of the server
            
        Returns:
            List of available model names
        """
        if server_name not in self.active_connections:
            if not await self.connect_to_server(server_name):
                return []
        
        try:
            if server_name == "ollama":
                response = requests.get(f"{self.servers[server_name]}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    return [model["name"] for model in data.get("models", [])]
            else:
                # Placeholder for other servers
                return ["gpt-4", "claude-3.5-sonnet", "gemini-pro"]
                
        except Exception as e:
            logger.error(f"Failed to list models for {server_name}: {e}")
            
        return []
    
    async def generate_response(self, server: str, model: str, prompt: str) -> str:
        """
        Generate response using specific model via MCP
        
        Args:
            server: Server name to use
            model: Model name to use
            prompt: Input prompt
            
        Returns:
            Generated response
        """
        if server not in self.active_connections:
            if not await self.connect_to_server(server):
                raise Exception(f"Cannot connect to server: {server}")
        
        try:
            if server == "ollama":
                return await self._generate_ollama_response(model, prompt)
            else:
                # Placeholder for other servers
                return f"Response from {model} on {server}: {prompt[:50]}..."
                
        except Exception as e:
            logger.error(f"Failed to generate response from {server}/{model}: {e}")
            raise
    
    async def _generate_ollama_response(self, model: str, prompt: str) -> str:
        """Generate response using Ollama API"""
        url = f"{self.servers['ollama']}/api/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return data.get("response", "No response received")
            
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            raise
    
    def get_connected_servers(self) -> List[str]:
        """Get list of currently connected servers"""
        return list(self.active_connections.keys())
    
    def get_server_status(self) -> Dict[str, Any]:
        """Get status of all configured servers"""
        status = {}
        for server_name, server_url in self.servers.items():
            status[server_name] = {
                "url": server_url,
                "connected": server_name in self.active_connections,
                "last_check": None  # We'll implement this later
            }
        return status
