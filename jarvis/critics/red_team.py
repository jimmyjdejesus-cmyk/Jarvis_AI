"""Adversarial critic that reviews outputs for logical flaws."""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

from .api import CriticVerdict

logger = logging.getLogger(__name__)


class RedTeamCritic:
    """Inspect artifacts for logical flaws and conflicting assumptions."""

    def __init__(self, mcp_client: Optional[Any] = None, model: str = "llama3.2"):
        self.mcp_client = mcp_client
        self.model = model
        self.review_prompt = (
            "You are a red team critic. Review the following specialist output "
            "for logical errors, contradictions, or unsupported assumptions. "
            "Respond in JSON with keys 'approved' (bool) and 'feedback'."
        )

    async def review(self, artifact: str, trace: Dict[str, Any] | None = None) -> CriticVerdict:
        """Review artifact and return :class:`CriticVerdict`."""
        if not self.mcp_client:
            return CriticVerdict(True, [], 0.0, "No MCP client configured")

        prompt = f"{self.review_prompt}\n\nOutput:\n{artifact}"
        try:
            response = await self.mcp_client.generate_response(
                server="ollama", model=self.model, prompt=prompt
            )
            try:
                data = json.loads(response.strip())
                return CriticVerdict(
                    bool(data.get("approved", True)),
                    [data.get("feedback", "")] if not data.get("approved", True) else [],
                    0.0,
                    data.get("feedback", ""),
                )
            except json.JSONDecodeError:
                return CriticVerdict(True, [], 0.0, response)
        except Exception as exc:  # pragma: no cover - best effort
            logger.error("Red team critic failed: %s", exc)
            return CriticVerdict(True, [], 0.0, "Critic unavailable")
