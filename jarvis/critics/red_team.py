"""Adversarial critic that reviews outputs for logical flaws.

The red team critic acts as an adversarial reviewer that inspects text
produced by specialist agents and highlights logical errors or conflicting
assumptions. It returns structured feedback indicating whether the content
was approved and any revision notes.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class RedTeamCritic:
    """Inspect specialist outputs for logical flaws and conflicts.

    Parameters
    ----------
    mcp_client : optional
        Client providing ``generate_response``. When ``None`` the critic
        always approves the content.
    model : str, optional
        Model name used when generating reviews. Defaults to ``"llama3.2"``.
    """

    def __init__(self, mcp_client: Optional[Any] = None, model: str = "llama3.2"):
        self.mcp_client = mcp_client
        self.model = model
        self.review_prompt = (
            "You are a red team critic. Review the following specialist output "
            "for logical errors, contradictions, or unsupported assumptions. "
            "Respond in JSON with keys 'approved' (bool) and 'feedback'."
        )

    async def review(self, specialist: str, content: str) -> Dict[str, Any]:
        """Review specialist content and return approval or revision feedback.

        Parameters
        ----------
        specialist: str
            Name of the specialist who produced the content.
        content: str
            The specialist's output to evaluate.

        Returns
        -------
        Dict[str, Any]
            Dictionary with ``approved`` boolean and ``feedback`` message.
        """
        if not self.mcp_client:
            return {"approved": True, "feedback": "No MCP client configured"}

        prompt = f"{self.review_prompt}\n\nSpecialist: {specialist}\nOutput:\n{content}"
        try:
            response = await self.mcp_client.generate_response(
                server="ollama", model=self.model, prompt=prompt
            )
            try:
                return json.loads(response.strip())
            except json.JSONDecodeError:
                return {"approved": True, "feedback": response}
        except Exception as exc:  # pragma: no cover - best effort
            logger.error("Red team critic failed: %s", exc)
            return {"approved": True, "feedback": "Critic unavailable"}
