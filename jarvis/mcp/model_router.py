"""Model routing based on declared intent.

This router maps high level intents to ordered sequences of models.  Each
model is represented by a ``(server, model)`` tuple which is tried in order
until one succeeds.  If all remote options fail a health‑checked fallback to
the local Ollama server is attempted.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Tuple

from .client import MCPClient, MCPError

logger = logging.getLogger(__name__)


class ModelRouter:
    """Simple intent → model routing with health‑checked fallback."""

    def __init__(self, mcp_client: MCPClient) -> None:
        self.mcp_client = mcp_client
        # Intents map to ordered sequences of (server, model)
        self.intent_map: Dict[str, List[Tuple[str, str]]] = {
            "code_review": [("openai", "gpt-4"), ("anthropic", "claude-3.5-sonnet")],
            "code_generation": [
                ("anthropic", "claude-3.5-sonnet"),
                ("openai", "gpt-4"),
            ],
            "general": [("openai", "gpt-3.5-turbo")],
        }
        # Local fallback (Ollama) used when all remote models fail
        self.local_fallback: Tuple[str, str] = ("ollama", "llama3.2")
        # Justification for last routing decision (shown in UI tooltip)
        self.last_justification: str = ""

    def _select_model(
        self, task_type: str, complexity: str, budget: str
    ) -> Tuple[Tuple[str, str], str]:
        """Pick a model based on task, complexity and budget policy."""

        if budget == "aggressive" or complexity == "high":
            pair = ("openai", "gpt-4")
            reason = "aggressive budget/high complexity → GPT-4"
        elif budget == "balanced":
            pair = ("openai", "gpt-3.5-turbo")
            reason = "balanced budget → GPT-3.5"
        else:
            pair = self.local_fallback
            reason = "conservative budget/low complexity → local model"

        return pair, reason

    async def route(self, intent: str, prompt: str) -> str:
        """Route ``prompt`` according to ``intent``.

        Parameters
        ----------
        intent:
            High level task type, e.g. ``"code_review"`` or ``"general"``.
        prompt:
            User provided text to send to the model.

        Returns
        -------
        str
            Model response.
        """

        sequence = self.intent_map.get(intent, self.intent_map["general"])
        last_error: Exception | None = None

        for server, model in sequence:
            healthy = await self.mcp_client.check_server_health(server)
            if not healthy:
                logger.warning("Server %s unhealthy; skipping", server)
                continue
            try:
                return await self.mcp_client.generate_response(server, model, prompt)
            except MCPError as exc:  # pragma: no cover - handled by router
                logger.warning("Model %s on %s failed: %s", model, server, exc)
                last_error = exc

        # All remote models failed – attempt local fallback
        if await self.mcp_client.check_server_health(self.local_fallback[0]):
            server, model = self.local_fallback
            self.last_justification = "fallback to local model"
            return await self.mcp_client.generate_response(server, model, prompt)

        raise MCPError(
            f"No available models for intent '{intent}'. Last error: {last_error}"
        )

    def update_intent(self, intent: str, sequence: List[Tuple[str, str]]) -> None:
        """Update or add a routing sequence for an intent."""

        self.intent_map[intent] = sequence

    async def route_to_best_model(
        self,
        message: str,
        force_local: bool = False,
        task_type: str = "general",
        complexity: str = "medium",
        budget: str = "balanced",
    ) -> str:
        """Route ``message`` using policy inputs.

        The selection justification is stored in ``last_justification`` for UI
        tooltip display.
        """

        if force_local:
            server, model = self.local_fallback
            reason = "forced local execution"
        else:
            (server, model), reason = self._select_model(task_type, complexity, budget)

        self.last_justification = reason
        logger.info("Model selection: %s/%s (%s)", server, model, reason)
        return await self.mcp_client.generate_response(server, model, message)

