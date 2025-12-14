"""
Intelligent model routing based on model capabilities, cost, and user preferences.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

from .client import MCPClient, MCPError
from .providers.openrouter import OpenRouterClient

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
        self.openrouter = OpenRouterClient()

        # CLOUD-FIRST CONFIGURATION
        self.strategy = os.getenv("ROUTE_STRATEGY", "cloud_first")
        self.prefer_free = os.getenv("PREFER_FREE_CLOUD", "true") == "true"
        self.allow_local_fallback = os.getenv("ALLOW_LOCAL_FALLBACK", "true") == "true"

        self.models: Dict[str, ModelMetadata] = {
            # Cloud models (via OpenRouter)
            "openrouter-llama-free": ModelMetadata(
                server="openrouter", context_window=8192, cost_per_token=0.0,
                quality_score=0.6, strengths=["general", "fast", "free"]
            ),
            "openrouter-claude": ModelMetadata(
                server="openrouter", context_window=200000, cost_per_token=0.8,
                quality_score=0.95, strengths=["coding", "reasoning", "complex"]
            ),
            "openrouter-gpt4o": ModelMetadata(
                server="openrouter", context_window=128000, cost_per_token=0.6,
                quality_score=0.9, strengths=["coding", "general", "reasoning"]
            ),

            # Local models (fallback)
            "llama3.2": ModelMetadata(
                server="ollama", context_window=8192, cost_per_token=0.1, quality_score=0.6,
                strengths=["general", "fast", "local"]
            ),
            "llama3": ModelMetadata(
                server="ollama", context_window=8192, cost_per_token=0.15, quality_score=0.7,
                strengths=["general", "reasoning", "local"]
            ),
        }
        self.last_justification: str = ""

    def _classify_complexity(self, prompt: str, task_type: str) -> str:
        """Auto-classify task complexity"""
        prompt_len = len(prompt)
        prompt_lower = prompt.lower()

        # High complexity keywords
        high_kw = ["architecture", "design", "audit", "security", "refactor", "system", "database"]
        if any(kw in prompt_lower for kw in high_kw) or prompt_len > 2000:
            return "high"

        # Medium complexity keywords
        medium_kw = ["write", "create", "implement", "debug", "review", "analyze", "explain"]
        if any(kw in prompt_lower for kw in medium_kw) or prompt_len > 500:
            return "medium"

        return "low"

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
        complexity: str = None,
    ) -> str:
        """
        CLOUD-FIRST routing: Try cloud models first, fallback to local only if cloud fails.
        """
        # Auto-detect complexity if not provided
        if not complexity:
            complexity = self._classify_complexity(prompt, task_type)

        logger.info(f"Routing: task={task_type}, complexity={complexity}, strategy={self.strategy}")

        # Force local override
        if force_local:
            self.last_justification = "Forced local execution."
            return await self._route_local(prompt, complexity)

        # CLOUD-FIRST: Try OpenRouter first
        if self.strategy in ["cloud_first", "balanced"]:
            try:
                model = self.openrouter.get_model_for_complexity(complexity)
                logger.info(f"Trying cloud first: {model}")

                result = await self.openrouter.generate(
                    prompt, model=model, complexity=complexity
                )

                self.last_justification = f"Cloud-first routing: {model} (complexity: {complexity})"
                return result

            except Exception as e:
                logger.warning(f"Cloud routing failed: {e}")

        # FALLBACK: Use local Ollama only if cloud fails or local-first strategy
        if self.allow_local_fallback or self.strategy == "local_first":
            logger.info("Cloud failed or local-first strategy, using local Ollama")
            return await self._route_local(prompt, complexity)

        raise MCPError("All routing options exhausted and local fallback disabled")

    async def _route_local(self, prompt: str, complexity: str) -> str:
        """Route to local Ollama models based on complexity"""
        if complexity == "high":
            model = "llama3"  # Best local option for complex tasks
            self.last_justification = f"Local fallback for high complexity: {model}"
        elif complexity == "medium":
            model = "llama3"  # Good balance for medium tasks
            self.last_justification = f"Local fallback for medium complexity: {model}"
        else:  # low
            model = "llama3.2"  # Fast for simple tasks
            self.last_justification = f"Local fallback for low complexity: {model}"

        try:
            return await self.mcp_client.generate_response("ollama", model, prompt)
        except MCPError as e:
            logger.error(f"Local routing failed: {e}")
            raise

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
