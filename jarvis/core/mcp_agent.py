"""
MCP-Aware Jarvis Agent with multi-model capabilities
"""
import asyncio
import logging
from typing import Optional, Dict, Any
from ..mcp import MCPClient, ModelRouter, MCPServerManager

logger = logging.getLogger(__name__)

class MCPJarvisAgent:
    """Enhanced Jarvis agent with MCP capabilities"""
    
    def __init__(self, enable_mcp: bool = True, enable_multi_agent: bool = False, fallback_model: str = "llama3.2"):
        """
        Initialize MCP-aware Jarvis agent
        
        Args:
            enable_mcp: Whether to enable MCP functionality
            enable_multi_agent: Whether to enable multi-agent capabilities (future)
            fallback_model: Model to use as fallback
        """
        self.enable_mcp = enable_mcp
        self.enable_multi_agent = enable_multi_agent  # For future use
        self.fallback_model = fallback_model
        self.conversation_history = []
        self.mcp_initialized = False
        
        if enable_mcp:
            try:
                self.mcp_client = MCPClient()
                self.server_manager = MCPServerManager(self.mcp_client)
                self.model_router = ModelRouter(self.mcp_client)
                logger.info("MCP components initialized")
            except Exception as e:
                logger.error(f"Failed to initialize MCP components: {e}")
                self.enable_mcp = False
        
        # Keep backward compatibility with simple agent
        try:
            from .simple_agent import JarvisAgent as SimpleAgent
            self.simple_agent = SimpleAgent()
            logger.info("Simple agent fallback available")
        except ImportError as e:
            logger.warning(f"Simple agent not available: {e}")
            self.simple_agent = None
    
    async def _ensure_mcp_initialized(self):
        """Ensure MCP is properly initialized"""
        if not self.enable_mcp:
            return False
            
        if not self.mcp_initialized:
            try:
                # Initialize server connections
                connection_results = await self.server_manager.initialize_all_servers()
                
                healthy_servers = [
                    server for server, success in connection_results.items() 
                    if success
                ]
                
                if healthy_servers:
                    self.mcp_initialized = True
                    logger.info(f"MCP initialized with servers: {healthy_servers}")
                    return True
                else:
                    logger.warning("No healthy servers available, MCP disabled")
                    self.enable_mcp = False
                    return False
                    
            except Exception as e:
                logger.error(f"MCP initialization failed: {e}")
                self.enable_mcp = False
                return False
        
        return True
    
    async def chat_async(self, message: str, use_mcp: bool = None, force_local: bool = False) -> str:
        """
        Async chat with MCP routing
        
        Args:
            message: User message
            use_mcp: Override MCP usage (None uses instance setting)
            force_local: Force use of local models only
            
        Returns:
            AI response
        """
        use_mcp = use_mcp if use_mcp is not None else self.enable_mcp
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": message,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        response = None
        error_msg = None
        
        # Try MCP routing first
        if use_mcp:
            try:
                if await self._ensure_mcp_initialized():
                    logger.info("Using MCP routing for message")
                    response = await self.model_router.route_to_best_model(message, force_local)
                    
                    # Add successful response to history
                    self.conversation_history.append({
                        "role": "assistant", 
                        "content": response,
                        "timestamp": asyncio.get_event_loop().time(),
                        "source": "mcp"
                    })
                    
                    return response
                    
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"MCP routing failed: {e}, falling back to simple agent")
        
        # Fallback to simple agent
        if self.simple_agent:
            try:
                logger.info("Using simple agent fallback")
                response = self.simple_agent.chat(message)
                
                # Add fallback response to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response, 
                    "timestamp": asyncio.get_event_loop().time(),
                    "source": "simple_agent"
                })
                
                return response
                
            except Exception as e:
                logger.error(f"Simple agent also failed: {e}")
                error_msg = f"MCP error: {error_msg}, Simple agent error: {str(e)}"
        
        # If everything failed
        fallback_response = f"""I apologize, but I'm experiencing technical difficulties. 

**Error Details:**
{error_msg or 'All AI systems are currently unavailable'}

**What you can try:**
1. Check if Ollama is running: `ollama serve`
2. Test local connection: `curl http://localhost:11434/api/tags`
3. Restart the Jarvis agent

**Your message:** {message}

I'll keep trying to respond once the connection is restored."""

        self.conversation_history.append({
            "role": "assistant",
            "content": fallback_response,
            "timestamp": asyncio.get_event_loop().time(),
            "source": "error_fallback"
        })
        
        return fallback_response
    
    def chat(self, message: str, use_mcp: bool = None, force_local: bool = False) -> str:
        """
        Synchronous wrapper for backward compatibility
        
        Args:
            message: User message
            use_mcp: Override MCP usage
            force_local: Force local models only
            
        Returns:
            AI response
        """
        try:
            # Handle existing event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're in an async context, need to use thread executor
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        lambda: asyncio.run(self.chat_async(message, use_mcp, force_local))
                    )
                    return future.result(timeout=60)
            else:
                # No event loop running, safe to use asyncio.run
                return asyncio.run(self.chat_async(message, use_mcp, force_local))
                
        except Exception as e:
            logger.error(f"Sync chat wrapper failed: {e}")
            
            # Final fallback - direct simple agent call
            if self.simple_agent:
                try:
                    return self.simple_agent.chat(message)
                except Exception as e2:
                    logger.error(f"Final fallback failed: {e2}")
            
            return f"I'm sorry, I'm having trouble processing your request: {message}"
    
    def get_conversation_history(self) -> list:
        """Get conversation history"""
        return self.conversation_history.copy()
    
    def clear_conversation_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")

    def get_mcp_status(self) -> Dict[str, Any]:
        """Get MCP system status"""
        if not self.enable_mcp:
            return {"enabled": False, "reason": "MCP disabled"}
        
        if not hasattr(self, 'server_manager'):
            return {"enabled": False, "reason": "MCP not initialized"}
        
        try:
            status_report = self.server_manager.get_server_status_report()
            
            return {
                "enabled": True,
                "initialized": self.mcp_initialized,
                "server_status": status_report,
                "healthy_servers": self.server_manager.get_healthy_servers(),
                "available_models": self.model_router.get_available_models() if hasattr(self, 'model_router') else {}
            }
        except Exception as e:
            return {"enabled": True, "error": str(e)}
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities"""
        capabilities = {
            "mcp_enabled": self.enable_mcp,
            "mcp_initialized": self.mcp_initialized if self.enable_mcp else False,
            "simple_agent_available": self.simple_agent is not None,
            "conversation_history_length": len(self.conversation_history)
        }
        
        if self.enable_mcp and hasattr(self, 'server_manager'):
            try:
                capabilities.update({
                    "healthy_servers": self.server_manager.get_healthy_servers(),
                    "available_models": self.model_router.get_available_models()
                })
            except:
                pass
        
        return capabilities
    
    def enable_mcp_mode(self):
        """Enable MCP mode"""
        self.enable_mcp = True
        self.mcp_initialized = False  # Force re-initialization
        logger.info("MCP mode enabled")
    
    def disable_mcp_mode(self):
        """Disable MCP mode - use simple agent only"""
        self.enable_mcp = False
        logger.info("MCP mode disabled, using simple agent only")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        health = {
            "overall_status": "unknown",
            "simple_agent": False,
            "mcp_system": False,
            "details": {}
        }
        
        # Test simple agent
        if self.simple_agent:
            try:
                test_response = self.simple_agent.chat("test")
                health["simple_agent"] = bool(test_response)
                health["details"]["simple_agent"] = "working"
            except Exception as e:
                health["details"]["simple_agent"] = f"error: {e}"
        
        # Test MCP system
        if self.enable_mcp:
            try:
                if await self._ensure_mcp_initialized():
                    test_response = await self.model_router.route_to_best_model("test", force_local=True)
                    health["mcp_system"] = bool(test_response)
                    health["details"]["mcp_system"] = "working"
                else:
                    health["details"]["mcp_system"] = "initialization failed"
            except Exception as e:
                health["details"]["mcp_system"] = f"error: {e}"
        
        # Determine overall status
        if health["mcp_system"]:
            health["overall_status"] = "excellent"
        elif health["simple_agent"]:
            health["overall_status"] = "good"
        else:
            health["overall_status"] = "poor"
        
        return health
