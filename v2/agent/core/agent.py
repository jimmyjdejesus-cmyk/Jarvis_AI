"""Minimal JarvisAgentV2 implementation used for testing and examples."""

from __future__ import annotations
from typing import Any, AsyncGenerator, Dict, Union

from v2.config.config import Config, load_config
from jarvis.logging.logger import get_logger
from jarvis.mcp import MCPClient
from jarvis.orchestration.orchestrator import MultiAgentOrchestrator

class JarvisAgentV2:
    """Minimal agent that delegates work to the orchestrator."""

    def __init__(self, config: Union[Config, Dict[str, Any], None] = None) -> None:
        if config is None:
            self.config = load_config()
        elif isinstance(config, Config):
            self.config = config
        else:
            self.config = Config(**config)
        self.agent_config = self.config.v2_agent
        self.logger = get_logger(__name__)

        # Initialize MCP client and orchestrator brain
        self.mcp_client = MCPClient()
        self.orchestrator = MultiAgentOrchestrator(mcp_client=self.mcp_client)

    # ------------------------------------------------------------------
    def setup_workflow(self) -> None:  # pragma: no cover - placeholder
        """Prepare the workflow."""

    # ------------------------------------------------------------------
    def run_workflow(self, query: str) -> Dict[str, Any]:
        """Return a minimal response for the given query."""

        return {"query": query, "result": "ok"}

    # ------------------------------------------------------------------
    async def stream_workflow(
        self, query: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Yield a single fake event for streaming tests."""

        yield {"step": "start", "query": query}

    # ------------------------------------------------------------------
    async def handle_request(
        self, request: str, code: str | None = None, user_context: str | None = None
    ) -> Dict[str, Any]:
        self.logger.info(f"Delegating request to MultiAgentOrchestrator: {request}")
        result = await self.orchestrator.coordinate_specialists(
            request=request,
            code=code,
            user_context=user_context,
        )
        return result


__all__ = ["JarvisAgentV2"]