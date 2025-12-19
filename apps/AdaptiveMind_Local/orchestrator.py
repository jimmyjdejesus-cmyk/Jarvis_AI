# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/

"""Compatibility wrapper for the legacy orchestrator.

This module provides a backward compatibility layer that delegates to the
sophisticated MultiAgentOrchestrator while maintaining the legacy API.

DEPRECATED: This compatibility layer will be removed in a future release.
Please migrate to using adaptivemind.orchestration.MultiAgentOrchestrator directly.
"""

from __future__ import annotations

from logger_config import log
from adaptivemind.orchestration.compat import LocalOrchestratorAdapter


class Orchestrator(LocalOrchestratorAdapter):
    """Compatibility wrapper for the legacy orchestrator.
    
    This class provides backward compatibility with the original
    `apps.AdaptiveMind_Local.Orchestrator` while delegating to the
    sophisticated `adaptivemind.orchestration.MultiAgentOrchestrator`.
    
    Note:
        This class is deprecated and will be removed in a future release.
        Please migrate to using `adaptivemind.orchestration.MultiAgentOrchestrator` directly.
    """
    
    def __init__(self, mcp_client=None):
        """Initialize the compatibility wrapper.
        
        Args:
            mcp_client: MCP client for the underlying orchestrator
        """
        super().__init__(mcp_client=mcp_client)
        log.info("Initialized legacy Orchestrator compatibility wrapper")
    
    def handle_request(self, request: str) -> tuple[str, int, float]:
        """Handle a request using the legacy interface.
        
        This method maintains the same signature as the original Orchestrator
        for backward compatibility.
        
        Args:
            request: The request to process
            
        Returns:
            Tuple of (response_text, tokens_generated, avg_confidence)
        """
        return super().handle_request(request)
