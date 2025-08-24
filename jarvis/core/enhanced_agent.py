"""
Enhanced Jarvis Agent with Multi-Agent Coordination
The ultimate Jarvis experience with specialist agent orchestration
"""
import asyncio
import logging
from typing import Optional, Dict, Any, List
from ..mcp import MCPClient, ModelRouter, MCPServerManager
from ..ecosystem.meta_intelligence import ExecutiveAgent

logger = logging.getLogger(__name__)

class EnhancedJarvisAgent:
    """Fully enhanced Jarvis with multi-agent coordination capabilities"""
    
    def __init__(self, enable_mcp: bool = True, enable_multi_agent: bool = True):
        """
        Initialize enhanced Jarvis agent
        
        Args:
            enable_mcp: Whether to enable MCP functionality
            enable_multi_agent: Whether to enable multi-agent coordination
        """
        self.enable_mcp = enable_mcp
        self.enable_multi_agent = enable_multi_agent
        self.conversation_history = []
        self.mcp_initialized = False
        self.multi_agent_initialized = False
        
        # Initialize MCP components
        if enable_mcp:
            try:
                self.mcp_client = MCPClient()
                self.server_manager = MCPServerManager(self.mcp_client)
                self.model_router = ModelRouter(self.mcp_client)
                logger.info("MCP components initialized")
                
                # Initialize meta-agent orchestrator if enabled
                if enable_multi_agent:
                    self.orchestrator = ExecutiveAgent("meta")
                    logger.info("Meta-agent initialized")
                    
            except Exception as e:
                logger.error(f"Failed to initialize enhanced components: {e}")
                self.enable_mcp = False
                self.enable_multi_agent = False
        
        # Fallback agents
        try:
            from .simple_agent import JarvisAgent as SimpleAgent
            self.simple_agent = SimpleAgent()
            logger.info("Simple agent fallback available")
        except ImportError:
            logger.warning("Simple agent not available")
            self.simple_agent = None
        
        try:
            from .mcp_agent import MCPJarvisAgent
            self.mcp_agent = MCPJarvisAgent(enable_mcp=enable_mcp) if enable_mcp else None
            logger.info("MCP agent available")
        except ImportError:
            logger.warning("MCP agent not available")
            self.mcp_agent = None
    
    async def _ensure_systems_initialized(self):
        """Ensure all systems are properly initialized"""
        # Initialize MCP if not done
        if self.enable_mcp and not self.mcp_initialized:
            try:
                connection_results = await self.server_manager.initialize_all_servers()
                healthy_servers = [s for s, success in connection_results.items() if success]
                
                if healthy_servers:
                    self.mcp_initialized = True
                    logger.info(f"MCP initialized with servers: {healthy_servers}")
                else:
                    logger.warning("No healthy servers, disabling MCP")
                    self.enable_mcp = False
                    
            except Exception as e:
                logger.error(f"MCP initialization failed: {e}")
                self.enable_mcp = False
        
        # Initialize multi-agent if enabled
        if self.enable_multi_agent and self.enable_mcp and not self.multi_agent_initialized:
            try:
                # Test orchestrator health
                if hasattr(self, 'orchestrator'):
                    health = await self.orchestrator.health_check_specialists()
                    healthy_specialists = [
                        name for name, status in health['specialists'].items() 
                        if status.get('status') == 'healthy'
                    ]
                    
                    if healthy_specialists:
                        self.multi_agent_initialized = True
                        logger.info(f"Multi-agent system initialized with specialists: {healthy_specialists}")
                    else:
                        logger.warning("No healthy specialists, disabling multi-agent")
                        self.enable_multi_agent = False
                        
            except Exception as e:
                logger.error(f"Multi-agent initialization failed: {e}")
                self.enable_multi_agent = False
        
        return self.mcp_initialized or self.simple_agent is not None
    
    async def chat_async(self, message: str, code: str = None, force_simple: bool = False, use_multi_agent: bool = None) -> str:
        """
        Advanced chat with multi-agent coordination
        
        Args:
            message: User message
            code: Optional code to analyze
            force_simple: Force use of simple agent only
            use_multi_agent: Override multi-agent usage
            
        Returns:
            AI response with coordination details
        """
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": message,
            "code": code,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        # Force simple mode if requested
        if force_simple:
            return await self._simple_chat(message)
        
        # Ensure systems are initialized
        if not await self._ensure_systems_initialized():
            return await self._simple_chat(message)
        
        # Determine if multi-agent coordination is needed
        use_multi_agent = use_multi_agent if use_multi_agent is not None else self.enable_multi_agent
        
        if use_multi_agent and hasattr(self, 'orchestrator'):
            try:
                # Analyze if this needs multi-agent coordination
                complexity_analysis = await self.orchestrator.analyze_request_complexity(message, code)
                
                if complexity_analysis["specialists_needed"]:
                    logger.info(f"Using multi-agent coordination: {complexity_analysis['specialists_needed']}")
                    
                    # Use multi-agent coordination
                    result = await self.orchestrator.coordinate_specialists(message, code)
                    
                    # Format response for user
                    response = self._format_multi_agent_response(result, complexity_analysis)
                    
                    # Add to conversation history
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": response,
                        "source": "multi_agent",
                        "specialists_used": result.get("specialists_used", []),
                        "confidence": result.get("confidence", 0.7),
                        "timestamp": asyncio.get_event_loop().time()
                    })
                    
                    return response
                else:
                    logger.info("Simple request, using MCP routing")
                    
            except Exception as e:
                logger.warning(f"Multi-agent coordination failed: {e}, falling back to MCP")
        
        # Fall back to MCP routing
        if self.enable_mcp and hasattr(self, 'model_router'):
            try:
                response = await self.model_router.route_to_best_model(message)
                
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response,
                    "source": "mcp_routing",
                    "timestamp": asyncio.get_event_loop().time()
                })
                
                return response
                
            except Exception as e:
                logger.warning(f"MCP routing failed: {e}, falling back to simple agent")
        
        # Final fallback to simple agent
        return await self._simple_chat(message)
    
    async def _simple_chat(self, message: str) -> str:
        """Fallback to simple agent"""
        if self.simple_agent:
            try:
                response = self.simple_agent.chat(message)
                
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response,
                    "source": "simple_agent",
                    "timestamp": asyncio.get_event_loop().time()
                })
                
                return response
                
            except Exception as e:
                logger.error(f"Simple agent failed: {e}")
        
        # Absolute fallback
        fallback_response = f"""I apologize, but I'm experiencing technical difficulties with all AI systems.

**Your message:** {message}

**Troubleshooting steps:**
1. Check if Ollama is running: `ollama serve`
2. Verify connection: `curl http://localhost:11434/api/tags`
3. Restart Jarvis: `python -c "import jarvis; jarvis.get_jarvis_agent().chat('test')"`

I'll keep trying to respond once the connection is restored."""

        self.conversation_history.append({
            "role": "assistant",
            "content": fallback_response,
            "source": "error_fallback",
            "timestamp": asyncio.get_event_loop().time()
        })
        
        return fallback_response
    
    def _format_multi_agent_response(self, result: Dict[str, Any], complexity_analysis: Dict[str, Any]) -> str:
        """Format multi-agent coordination result for user"""
        
        if result.get("error"):
            return f"I encountered an error during multi-agent analysis: {result.get('coordination_summary', 'Unknown error')}"
        
        # Build response with coordination details
        response_parts = []
        
        # Header with coordination info
        specialists_used = result.get("specialists_used", [])
        confidence = result.get("confidence", 0.7)
        
        if len(specialists_used) > 1:
            response_parts.append(f"🧠 **Multi-Agent Analysis** ({len(specialists_used)} specialists)")
            response_parts.append(f"**Coordination:** {result.get('type', 'unknown').replace('_', ' ').title()}")
            response_parts.append(f"**Specialists:** {', '.join([s.replace('_', ' ').title() for s in specialists_used])}")
            response_parts.append(f"**Confidence:** {confidence:.1%}")
            response_parts.append("")
        
        # Main synthesized response
        synthesized_response = result.get("synthesized_response", "No response generated")
        response_parts.append("**Comprehensive Analysis:**")
        response_parts.append(synthesized_response)
        
        # Add individual specialist insights if available
        individual_results = result.get("results", {})
        if len(individual_results) > 1:
            response_parts.append("")
            response_parts.append("---")
            response_parts.append("**Individual Specialist Insights:**")
            
            for specialist_type, specialist_result in individual_results.items():
                if not specialist_result.get("error"):
                    specialist_confidence = specialist_result.get("confidence", 0.0)
                    response_parts.append(f"\n**{specialist_type.replace('_', ' ').title()} Expert** ({specialist_confidence:.1%} confidence):")
                    
                    # Add top suggestions
                    suggestions = specialist_result.get("suggestions", [])
                    if suggestions:
                        for suggestion in suggestions[:2]:  # Top 2 suggestions
                            response_parts.append(f"• {suggestion}")
        
        # Footer
        if len(specialists_used) > 1:
            response_parts.append("")
            response_parts.append("---")
            response_parts.append("*This response was created through coordinated analysis by multiple AI specialists for optimal accuracy and comprehensiveness.*")
        
        return "\n".join(response_parts)
    
    def chat(self, message: str, code: str = None, force_simple: bool = False, use_multi_agent: bool = None) -> str:
        """
        Synchronous wrapper for enhanced chat functionality
        
        Args:
            message: User message
            code: Optional code to analyze
            force_simple: Force simple mode
            use_multi_agent: Override multi-agent setting
            
        Returns:
            AI response
        """
        try:
            return asyncio.run(self.chat_async(message, code, force_simple, use_multi_agent))
        except Exception as e:
            logger.error(f"Enhanced chat failed: {e}")
            
            # Final fallback
            if self.simple_agent:
                try:
                    return self.simple_agent.chat(message)
                except:
                    pass
            
            return f"I'm sorry, I'm having trouble processing your request: {message}"
    
    def analyze_with_specialists(self, message: str, specialists: List[str] = None, code: str = None) -> Dict[str, Any]:
        """
        Explicitly request analysis from specific specialists
        
        Args:
            message: Message to analyze
            specialists: List of specialist types to use
            code: Optional code to include
            
        Returns:
            Detailed analysis results
        """
        if not self.enable_multi_agent or not hasattr(self, 'orchestrator'):
            return {"error": "Multi-agent system not available"}
        
        async def _analyze():
            if specialists:
                # Override analysis to use specified specialists
                analysis = {
                    "specialists_needed": specialists,
                    "complexity": "medium",
                    "coordination_type": "parallel" if len(specialists) <= 2 else "sequential"
                }
                
                # Force use of specified specialists
                original_method = self.orchestrator.analyze_request_complexity
                self.orchestrator.analyze_request_complexity = lambda *args: analysis
                
                try:
                    result = await self.orchestrator.coordinate_specialists(message, code)
                    return result
                finally:
                    # Restore original method
                    self.orchestrator.analyze_request_complexity = original_method
            else:
                return await self.orchestrator.coordinate_specialists(message, code)
        
        try:
            return asyncio.run(_analyze())
        except Exception as e:
            return {"error": str(e)}
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get comprehensive agent capabilities"""
        capabilities = {
            "mcp_enabled": self.enable_mcp,
            "mcp_initialized": self.mcp_initialized,
            "multi_agent_enabled": self.enable_multi_agent,
            "multi_agent_initialized": self.multi_agent_initialized,
            "simple_agent_available": self.simple_agent is not None,
            "conversation_history_length": len(self.conversation_history)
        }
        
        # Add MCP capabilities
        if self.enable_mcp and hasattr(self, 'server_manager'):
            try:
                capabilities.update({
                    "healthy_servers": self.server_manager.get_healthy_servers(),
                    "available_models": self.model_router.get_available_models() if hasattr(self, 'model_router') else {}
                })
            except:
                pass
        
        # Add multi-agent capabilities
        if self.enable_multi_agent and hasattr(self, 'orchestrator'):
            try:
                specialist_status = self.orchestrator.get_specialist_status()
                capabilities.update({
                    "available_specialists": specialist_status["available_specialists"],
                    "total_specialist_tasks": specialist_status["total_tasks_completed"]
                })
            except:
                pass
        
        return capabilities
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        status = {
            "timestamp": asyncio.get_event_loop().time(),
            "overall_status": "unknown",
            "systems": {}
        }
        
        # Simple agent status
        status["systems"]["simple_agent"] = {
            "available": self.simple_agent is not None,
            "status": "ready" if self.simple_agent else "unavailable"
        }
        
        # MCP system status
        if self.enable_mcp:
            if hasattr(self, 'server_manager'):
                mcp_status = self.server_manager.get_server_status_report()
                status["systems"]["mcp"] = {
                    "enabled": True,
                    "initialized": self.mcp_initialized,
                    "healthy_servers": mcp_status["healthy_servers"],
                    "total_servers": mcp_status["total_servers"]
                }
            else:
                status["systems"]["mcp"] = {"enabled": True, "status": "not_initialized"}
        else:
            status["systems"]["mcp"] = {"enabled": False}
        
        # Multi-agent system status
        if self.enable_multi_agent:
            status["systems"]["multi_agent"] = {
                "enabled": True,
                "initialized": self.multi_agent_initialized,
                "available_specialists": len(self.orchestrator.specialists) if hasattr(self, 'orchestrator') else 0
            }
        else:
            status["systems"]["multi_agent"] = {"enabled": False}
        
        # Determine overall status
        if self.multi_agent_initialized:
            status["overall_status"] = "excellent"
        elif self.mcp_initialized:
            status["overall_status"] = "good"
        elif self.simple_agent:
            status["overall_status"] = "basic"
        else:
            status["overall_status"] = "poor"
        
        return status
    
    def enable_simple_mode(self):
        """Switch to simple mode only"""
        self.enable_mcp = False
        self.enable_multi_agent = False
        logger.info("Switched to simple mode")
    
    def enable_smart_mode(self):
        """Enable MCP mode, disable multi-agent"""
        self.enable_mcp = True
        self.enable_multi_agent = False
        self.mcp_initialized = False  # Force re-initialization
        logger.info("Switched to smart (MCP) mode")
    
    def enable_super_mode(self):
        """Enable full multi-agent mode"""
        self.enable_mcp = True
        self.enable_multi_agent = True
        self.mcp_initialized = False  # Force re-initialization
        self.multi_agent_initialized = False
        logger.info("Switched to super (multi-agent) mode")
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check of all systems"""
        health = {
            "overall_status": "unknown",
            "systems": {},
            "timestamp": asyncio.get_event_loop().time()
        }
        
        # Test simple agent
        if self.simple_agent:
            try:
                test_response = self.simple_agent.chat("health check")
                health["systems"]["simple_agent"] = {
                    "status": "healthy",
                    "response_received": bool(test_response)
                }
            except Exception as e:
                health["systems"]["simple_agent"] = {"status": "error", "error": str(e)}
        else:
            health["systems"]["simple_agent"] = {"status": "unavailable"}
        
        # Test MCP system
        if self.enable_mcp and hasattr(self, 'model_router'):
            try:
                await self._ensure_systems_initialized()
                test_response = await self.model_router.route_to_best_model("health check", force_local=True)
                health["systems"]["mcp"] = {
                    "status": "healthy",
                    "initialized": self.mcp_initialized,
                    "response_received": bool(test_response)
                }
            except Exception as e:
                health["systems"]["mcp"] = {"status": "error", "error": str(e)}
        else:
            health["systems"]["mcp"] = {"status": "disabled"}
        
        # Test multi-agent system
        if self.enable_multi_agent and hasattr(self, 'orchestrator'):
            try:
                specialist_health = await self.orchestrator.health_check_specialists()
                health["systems"]["multi_agent"] = {
                    "status": specialist_health["overall_status"],
                    "initialized": self.multi_agent_initialized,
                    "healthy_specialists": len([
                        s for s in specialist_health["specialists"].values() 
                        if s.get("status") == "healthy"
                    ])
                }
            except Exception as e:
                health["systems"]["multi_agent"] = {"status": "error", "error": str(e)}
        else:
            health["systems"]["multi_agent"] = {"status": "disabled"}
        
        # Determine overall health
        if health["systems"].get("multi_agent", {}).get("status") == "healthy":
            health["overall_status"] = "excellent"
        elif health["systems"].get("mcp", {}).get("status") == "healthy":
            health["overall_status"] = "good"  
        elif health["systems"].get("simple_agent", {}).get("status") == "healthy":
            health["overall_status"] = "basic"
        else:
            health["overall_status"] = "poor"
        
        return health
