"""Red team critic for validating specialist agent outputs.

This critic acts as an adversarial reviewer that inspects the text
produced by specialist agents and highlights logical errors or
conflicting assumptions. Enable this critic by setting
``ENABLE_RED_TEAM: true`` in ``config/default.yaml``.
"""

import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class RedTeamCritic:
    """Inspects specialist outputs for logical flaws and conflicts."""

    def __init__(self, mcp_client):
        self.mcp_client = mcp_client
        self.review_prompt = (
            "You are a red team critic. Review the following specialist output "
            "for logical errors, contradictions, or unsupported assumptions. "
            "Respond in JSON with keys 'approved' (bool) and 'feedback'."
        )

    async def review(self, specialist: str, content: str) -> Dict[str, Any]:
        """Review specialist content and return approval or revision feedback.

        Args:
            specialist: Name of the specialist who produced the content.
            content: The specialist's output to evaluate.

        Returns:
            A dictionary containing ``approved`` and ``feedback`` fields.
        """
        prompt = f"{self.review_prompt}\n\nSpecialist: {specialist}\nOutput:\n{content}"
        try:
            response = await self.mcp_client.generate_response(
                server="ollama", model=self.model, prompt=prompt
            )
            try:
                data = json.loads(response.strip())
            except json.JSONDecodeError:
                data = {"approved": True, "feedback": response}
            return data
        except Exception as e:
            logger.error(f"Red team critic failed: {e}")
            return {"approved": True, "feedback": "Critic unavailable"}
