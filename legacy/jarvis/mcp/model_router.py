"""
Intelligent model routing based on model capabilities, cost, and user preferences.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

from .client import MCPClient, MCPError

logger = logging.getLogger(__name__)

@dataclass
class ModelMetadata:
    """Stores metadata about a specific model."""
    server: str
    context_window: int
    cost_per_token: float  # A normalized cost metric
    quality_score: float   # A normalized quality score (0.0 to 1.0)
    strengths: List[str]   # e.g., ['coding', 'summarization', 'general']

class ModelRouter:
    """Intelligently routes requests to the best model based on multiple factors."""

    def __init__(self, mcp_client: MCPClient) -> None:
        self.mcp_client = mcp_client
        self.models: Dict[str, ModelMetadata] = {
            "gpt-4": ModelMetadata(
                server="openai", context_window=8192, cost_per_token=0.9, quality_score=0.9,
                strengths=["coding", "general", "reasoning"]
            ),
            "claude-3.5-sonnet": ModelMetadata(
                server="anthropic", context_window=200000, cost_per_token=0.7, quality_score=0.85,
                strengths=["coding", "summarization", "long_context"]
            ),
            "gpt-3.5-turbo": ModelMetadata(
                server="openai", context_window=4096, cost_per_token=0.3, quality_score=0.7,
                strengths=["general", "fast"]
            ),
            "llama3.2": ModelMetadata(
                server="ollama", context_window=8192, cost_per_token=0.1, quality_score=0.6,
                strengths=["general", "fast", "local"]
            ),
        }
        self.last_justification: str = ""

    def _intelligent_route(
        self,
        prompt: str,
        task_type: str = "general",
        quality_vs_cost: float = 0.5,  # 0.0=cheapest, 1.0=highest quality
        excluded_servers: Optional[set] = None,
    ) -> Optional[Tuple[str, str]]:
        """
        Selects the best model by filtering based on constraints and scoring based on preference.
        """
        prompt_length = len(prompt)
        excluded_servers = excluded_servers or set()

        # 1. Filter by constraints (context window, task type, and excluded servers)
        candidate_models = []
        for name, meta in self.models.items():
            if meta.server in excluded_servers:
                continue
            if prompt_length > meta.context_window:
                continue
            if task_type != "general" and task_type not in meta.strengths:
                continue
            candidate_models.append((name, meta))

        if not candidate_models:
            self.last_justification = "No models available for the given constraints."
            return None

        # 2. Score remaining candidates based on quality vs. cost preference
        best_model = None
        max_score = -1.0

        for name, meta in candidate_models:
            # Score is a weighted average of quality and inverse cost
            # quality_vs_cost = 1.0 -> score is just quality
            # quality_vs_cost = 0.0 -> score is just inverse cost
            score = (meta.quality_score * quality_vs_cost) + ((1 - meta.cost_per_token) * (1 - quality_vs_cost))

            if score > max_score:
                max_score = score
                best_model = (meta.server, name)

        self.last_justification = f"Selected {best_model[1]} on {best_model[0]}. Score: {max_score:.2f} (Quality/Cost bias: {quality_vs_cost})"
        return best_model

    async def route_request(
        self,
        prompt: str,
        task_type: str = "general",
        quality_vs_cost: float = 0.5,
        force_local: bool = False,
    ) -> str:
        """
        Routes a prompt to the best available model based on intelligent routing,
        with health checks and a local fallback.
        """
        if force_local:
            self.last_justification = "Forced local execution."
            selected_model = ("ollama", "llama3.2")
            return await self.mcp_client.generate_response(selected_model[0], selected_model[1], prompt)

        excluded_servers = set()
        while len(excluded_servers) < len(self.models):
            selected_model = self._intelligent_route(prompt, task_type, quality_vs_cost, excluded_servers)

            if not selected_model:
                logger.warning("No suitable model found by router. Attempting local fallback.")
                break # Break to go to final fallback

            server, model_name = selected_model
            if await self.mcp_client.check_server_health(server):
                logger.info("Routing to %s/%s. Justification: %s", server, model_name, self.last_justification)
                try:
                    return await self.mcp_client.generate_response(server, model_name, prompt)
                except MCPError as e:
                    logger.warning("Model %s on %s failed: %s. Excluding server and retrying.", model_name, server, e)
                    excluded_servers.add(server)
            else:
                logger.warning("Selected server %s is unhealthy. Excluding and retrying.", server)
                excluded_servers.add(server)

        # Final fallback to local if all else fails
        logger.warning("All other options exhausted. Falling back to local model.")
        self.last_justification = "All preferred models/servers failed or were unhealthy. Falling back to local."
        local_server, local_model = ("ollama", "llama3.2")
        if await self.mcp_client.check_server_health(local_server):
            return await self.mcp_client.generate_response(local_server, local_model, prompt)

        raise MCPError("All available models and servers are unhealthy or have failed.")

    # Backwards compatibility alias
    async def route_to_best_model(
        self,
        prompt: str,
        force_local: bool = False,
        task_type: str = "general",
        quality_vs_cost: float = 0.5,
    ) -> str:
        """Alias for legacy callers expecting route_to_best_model.

        Kept for backwards compatibility with older agent code that
        calls `route_to_best_model`. This simply proxies into
        `route_request` using the same parameters.
        """
        return await self.route_request(
            prompt, task_type=task_type, quality_vs_cost=quality_vs_cost, force_local=force_local
        )
