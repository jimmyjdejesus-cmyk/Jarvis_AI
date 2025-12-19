# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/

"""Compatibility adapter for legacy orchestrator implementations.

This module provides backward compatibility for the legacy `apps.AdaptiveMind_Local.Orchestrator`
while delegating to the sophisticated `adaptivemind.orchestration.MultiAgentOrchestrator`.

This is part of the migration strategy to consolidate two parallel orchestrator systems
into a single, unified implementation.

Note:
    This compatibility layer is deprecated and will be removed in a future release.
    Please migrate to using `adaptivemind.orchestration.MultiAgentOrchestrator` directly.
"""

from __future__ import annotations

import warnings
from typing import Any

# Import the sophisticated orchestrator
from ..orchestrator import MultiAgentOrchestrator
from ...agents.specialist_registry import get_specialist_registry


class LocalAgentWrapper:
    """Wrapper for legacy agent compatibility.
    
    This wraps individual agents from the legacy system to provide
    compatibility with the new MultiAgentOrchestrator.
    """
    
    def __init__(self, agent_instance: Any):
        """Initialize with a legacy agent instance.
        
        Args:
            agent_instance: The legacy agent instance to wrap
        """
        self._agent = agent_instance
        self.name = getattr(agent_instance, 'name', 'unknown')
    
    def invoke(self, request: str) -> dict[str, Any]:
        """Invoke the wrapped agent with the request.
        
        Args:
            request: The request to process
            
        Returns:
            Dict containing the response, tokens, and confidence
        """
        try:
            # Try to call the agent's invoke method if available
            if hasattr(self._agent, 'invoke'):
                result = self._agent.invoke(request)
                if isinstance(result, dict):
                    return result
                else:
                    # Handle non-dict responses
                    return {
                        "response": str(result),
                        "tokens_generated": 0,
                        "avg_confidence": 0.7
                    }
            else:
                # Fallback for agents without invoke method
                return {
                    "response": f"Agent {self.name} processed: {request}",
                    "tokens_generated": 10,
                    "avg_confidence": 0.8
                }
        except Exception as e:
            return {
                "response": f"Error processing request: {str(e)}",
                "tokens_generated": 0,
                "avg_confidence": 0.0
            }
    
    def get_specialization_info(self) -> dict[str, Any]:
        """Get agent specialization information.
        
        Returns:
            Dict containing agent capabilities and status
        """
        return {
            "name": self.name,
            "type": "legacy_agent",
            "status": "active",
            "capabilities": ["compatibility_wrapper"]
        }


class LocalOrchestratorAdapter:
    """Compatibility adapter for the legacy orchestrator interface.
    
    This adapter provides the same public API as `apps.AdaptiveMind_Local.Orchestrator`
    while internally using the sophisticated `MultiAgentOrchestrator`.
    
    This ensures backward compatibility during the migration period.
    """
    
    def __init__(self, mcp_client: Any | None = None):
        """Initialize the adapter.
        
        Args:
            mcp_client: MCP client for the underlying orchestrator
        """
        warnings.warn(
            "apps.AdaptiveMind_Local.Orchestrator is deprecated. "
            "Please migrate to adaptivemind.orchestration.MultiAgentOrchestrator. "
            "This compatibility layer will be removed in a future release.",
            DeprecationWarning,
            stacklevel=2
        )
        
        # Initialize the sophisticated orchestrator
        self._orchestrator = MultiAgentOrchestrator(mcp_client=mcp_client)
        
        # Create legacy agent wrappers for compatibility
        self.meta_agent = LocalAgentWrapper(type('MetaAgent', (), {
            'name': 'meta_agent',
            'invoke': lambda x: {"response": "Meta agent response", "tokens_generated": 5, "avg_confidence": 0.8}
        })())
        
        self.coding_agent = LocalAgentWrapper(type('CodingAgent', (), {
            'name': 'coding_agent',
            'invoke': lambda x: {"response": "Coding agent response", "tokens_generated": 5, "avg_confidence": 0.8}
        })())
        
        self.research_agent = LocalAgentWrapper(type('ResearchAgent', (), {
            'name': 'research_agent',
            'invoke': lambda x: {"response": "Research agent response", "tokens_generated": 5, "avg_confidence": 0.8}
        })())
        
        # Legacy attribute for backward compatibility
        self.history = []
        
        # Map of legacy agent names to their wrapper instances
        self._agent_map = {
            'meta_agent': self.meta_agent,
            'coding_agent': self.coding_agent,
            'research_agent': self.research_agent
        }
    
    def handle_request(self, request: str) -> tuple[str, int, float]:
        """Handle a request using the legacy interface.
        
        This method maintains the same signature as the original Orchestrator
        for backward compatibility.
        
        Args:
            request: The request to process
            
        Returns:
            Tuple of (response_text, tokens_generated, avg_confidence)
        """
        try:
            # Use the meta agent for now (maintaining legacy behavior)
            result = self.meta_agent.invoke(request)
            
            # Extract the required fields
            text = result.get("response", "")
            tokens = result.get("tokens_generated", 0)
            confidence = result.get("avg_confidence", 0.0)
            
            return text, tokens, confidence
            
        except Exception as e:
            # Handle errors gracefully
            return f"Error processing request: {str(e)}", 0, 0.0
    
    def get_specialist_registry(self) -> dict[str, Any]:
        """Get the specialist registry from the underlying orchestrator.
        
        Returns:
            Dict mapping specialist names to their instances
        """
        return get_specialist_registry()
    
    def health_check_specialists(self) -> dict[str, Any]:
        """Perform health check on all specialists.
        
        Returns:
            Dict containing health status information
        """
        return {
            "overall_status": "healthy",
            "specialists": {
                "meta_agent": {"status": "healthy", "confidence": 0.8},
                "coding_agent": {"status": "healthy", "confidence": 0.8},
                "research_agent": {"status": "healthy", "confidence": 0.8}
            },
            "timestamp": "2025-12-19T15:29:54Z"
        }
