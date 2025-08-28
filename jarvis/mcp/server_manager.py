"""
MCP Server Manager for handling multiple model servers
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MCPServerManager:
    """Manages multiple MCP servers and their health"""
    
    def __init__(self, mcp_client):
        """
        Initialize server manager
        
        Args:
            mcp_client: MCP client instance
        """
        self.mcp_client = mcp_client
        self.server_health = {}
        self.last_health_check = {}
        self.health_check_interval = 300  # 5 minutes
        
        # Server configurations
        self.server_configs = {
            "ollama": {
                "url": "http://localhost:11434",
                "type": "local",
                "models": ["llama3.2", "llama3.1", "llama3"],
                "priority": 1,
                "timeout": 30
            },
            "openai": {
                "url": "https://api.openai.com/v1",
                "type": "remote",
                "models": ["gpt-4", "gpt-3.5-turbo"],
                "priority": 2,
                "timeout": 60,
                "requires_api_key": True
            },
            "anthropic": {
                "url": "https://api.anthropic.com/v1",
                "type": "remote", 
                "models": ["claude-3.5-sonnet", "claude-3"],
                "priority": 2,
                "timeout": 60,
                "requires_api_key": True
            },
            "google": {
                "url": "https://generativelanguage.googleapis.com/v1",
                "type": "remote",
                "models": ["gemini-pro"],
                "priority": 3,
                "timeout": 60,
                "requires_api_key": True
            }
        }
    
    async def initialize_all_servers(self) -> Dict[str, bool]:
        """
        Initialize connections to all configured servers
        
        Returns:
            Dictionary mapping server names to connection success
        """
        results = {}
        
        for server_name in self.server_configs:
            try:
                success = await self.mcp_client.connect_to_server(server_name)
                results[server_name] = success
                
                if success:
                    logger.info(f"Successfully connected to {server_name}")
                    await self._update_server_health(server_name, "healthy")
                else:
                    logger.warning(f"Failed to connect to {server_name}")
                    await self._update_server_health(server_name, "unreachable")
                    
            except Exception as e:
                logger.error(f"Error connecting to {server_name}: {e}")
                results[server_name] = False
                await self._update_server_health(server_name, "error")
        
        return results
    
    async def health_check_all_servers(self) -> Dict[str, str]:
        """
        Perform health check on all servers
        
        Returns:
            Dictionary mapping server names to health status
        """
        health_results = {}
        
        for server_name in self.server_configs:
            health_status = await self.check_server_health(server_name)
            health_results[server_name] = health_status
        
        return health_results
    
    async def check_server_health(self, server_name: str) -> str:
        """
        Check health of a specific server
        
        Args:
            server_name: Name of server to check
            
        Returns:
            Health status: 'healthy', 'degraded', 'unreachable', 'error'
        """
        if server_name not in self.server_configs:
            return "unknown"
        
        # Check if we need to perform health check
        if not self._should_health_check(server_name):
            return self.server_health.get(server_name, "unknown")
        
        try:
            # Perform actual health check
            config = self.server_configs[server_name]
            
            if server_name == "ollama":
                # For Ollama, try to list models
                models = await self.mcp_client.list_models(server_name)
                if models:
                    status = "healthy"
                else:
                    status = "degraded"
            else:
                # For other servers, try basic connection
                connected = await self.mcp_client.connect_to_server(server_name)
                status = "healthy" if connected else "unreachable"
            
            await self._update_server_health(server_name, status)
            return status
            
        except Exception as e:
            logger.error(f"Health check failed for {server_name}: {e}")
            await self._update_server_health(server_name, "error")
            return "error"
    
    def _should_health_check(self, server_name: str) -> bool:
        """Check if server needs health check based on interval"""
        if server_name not in self.last_health_check:
            return True
        
        last_check = self.last_health_check[server_name]
        now = datetime.now()
        
        return (now - last_check).total_seconds() > self.health_check_interval
    
    async def _update_server_health(self, server_name: str, status: str):
        """Update server health status and timestamp"""
        self.server_health[server_name] = status
        self.last_health_check[server_name] = datetime.now()
    
    def get_healthy_servers(self) -> List[str]:
        """Get list of currently healthy servers"""
        healthy = []
        for server_name, status in self.server_health.items():
            if status == "healthy":
                healthy.append(server_name)
        return healthy
    
    def get_servers_by_priority(self, include_unhealthy: bool = False) -> List[str]:
        """
        Get servers ordered by priority
        
        Args:
            include_unhealthy: Whether to include unhealthy servers
            
        Returns:
            List of server names in priority order
        """
        servers = []
        
        # Sort by priority (lower number = higher priority)
        sorted_servers = sorted(
            self.server_configs.items(),
            key=lambda x: x[1]["priority"]
        )

        for server_name, config in sorted_servers:
            if include_unhealthy:
                servers.append(server_name)
            else:
                status = self.server_health.get(server_name, "unknown")
                if status in ["healthy", "degraded"]:
                    servers.append(server_name)
        
        return servers
    
    def get_servers_for_model(self, model: str) -> List[str]:
        """
        Get servers that support a specific model
        
        Args:
            model: Model name to find
            
        Returns:
            List of server names that support the model
        """
        supporting_servers = []
        
        for server_name, config in self.server_configs.items():
            if model in config.get("models", []):
                # Check if server is healthy
                status = self.server_health.get(server_name, "unknown")
                if status in ["healthy", "degraded"]:
                    supporting_servers.append(server_name)
        
        # Sort by priority
        supporting_servers.sort(
            key=lambda x: self.server_configs[x]["priority"]
        )
        
        return supporting_servers
    
    def get_server_status_report(self) -> Dict[str, Any]:
        """
        Get comprehensive status report of all servers
        
        Returns:
            Detailed status information
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_servers": len(self.server_configs),
            "healthy_servers": len(self.get_healthy_servers()),
            "servers": {}
        }
        
        for server_name, config in self.server_configs.items():
            status = self.server_health.get(server_name, "unknown")
            last_check = self.last_health_check.get(server_name)
            
            report["servers"][server_name] = {
                "status": status,
                "type": config["type"],
                "priority": config["priority"],
                "models": config["models"],
                "last_health_check": last_check.isoformat() if last_check else None,
                "requires_api_key": config.get("requires_api_key", False),
                "url": config["url"]
            }
        
        return report
    
    async def start_health_monitoring(self):
        """Start background health monitoring task"""
        async def monitor_loop():
            while True:
                try:
                    await self.health_check_all_servers()
                    await asyncio.sleep(self.health_check_interval)
                except Exception as e:
                    logger.error(f"Health monitoring error: {e}")
                    await asyncio.sleep(60)  # Shorter retry on error
        
        # Start monitoring task
        asyncio.create_task(monitor_loop())
        logger.info("Started server health monitoring")
    
    def add_server(self, name: str, config: Dict[str, Any]):
        """
        Add a new server configuration
        
        Args:
            name: Server name
            config: Server configuration dictionary
        """
        required_keys = ["url", "type", "models", "priority"]
        if not all(key in config for key in required_keys):
            raise ValueError(f"Server config must include: {required_keys}")
        
        self.server_configs[name] = config
        logger.info(f"Added server configuration: {name}")
    
    def remove_server(self, name: str):
        """Remove a server configuration"""
        if name in self.server_configs:
            del self.server_configs[name]
            if name in self.server_health:
                del self.server_health[name]
            if name in self.last_health_check:
                del self.last_health_check[name]
            logger.info(f"Removed server: {name}")
    
    def update_server_priority(self, name: str, priority: int):
        """Update server priority"""
        if name in self.server_configs:
            self.server_configs[name]["priority"] = priority
            logger.info(f"Updated {name} priority to {priority}")
