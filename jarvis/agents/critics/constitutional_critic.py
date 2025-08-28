"""Constitutional critic that vetoes plans violating safety policies."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List

import yaml

logger = logging.getLogger(__name__)


@dataclass
class ConstitutionalCritic:
    """Review mission plans against a safety constitution."""

    mcp_client: Any
    constitution_path: str = "policies/safety.yaml"
    constitution: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Load the constitution from YAML."""
        try:
            with open(self.constitution_path, "r", encoding="utf-8") as f:
                self.constitution = yaml.safe_load(f) or {}
        except FileNotFoundError:  # pragma: no cover - config is optional
            logger.warning("Constitution file %s not found", self.constitution_path)
            self.constitution = {}

    async def review(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Check a mission plan for constitution violations using an LLM."""
        plan_text = json.dumps(plan)
        constitution_text = json.dumps(self.constitution)

        prompt = f"""
As a constitutional critic, your task is to review a mission plan against a given constitution.
The constitution defines a set of rules and principles that must be followed.

**Constitution:**
{constitution_text}

**Mission Plan:**
{plan_text}

Analyze the mission plan and determine if it violates any of the principles in the constitution.
Respond with a JSON object containing two keys:
1. "veto": A boolean indicating whether the plan should be vetoed (true if there are violations).
2. "violations": A list of strings, where each string is a specific violation found in the plan. If there are no violations, this should be an empty list.

Example of a valid response:
{{
  "veto": true,
  "violations": ["The plan involves accessing sensitive user data without consent, which violates the 'User Privacy' principle."]
}}

JSON Response:
"""
        try:
            response_str = await self.mcp_client.generate_response("ollama", "llama3.2", prompt)
            review = json.loads(response_str)
            if not isinstance(review.get("veto"), bool) or not isinstance(review.get("violations"), list):
                raise ValueError("Invalid JSON structure from critic model")
            return review
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to review mission plan: {e}")
            return {"veto": True, "violations": ["Failed to get a valid review from the critic model."]}
