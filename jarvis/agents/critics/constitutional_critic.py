"""Constitutional critic that vetoes plans violating safety policies."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List

import yaml

logger = logging.getLogger(__name__)


@dataclass
class ConstitutionalCritic:
    """Review mission plans against a safety constitution."""

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

    def review(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Check a mission plan for constitution violations."""
        plan_text = json.dumps(plan).lower()
        blocked: List[str] = self.constitution.get("blocked_phrases", [])
        violations = [phrase for phrase in blocked if phrase.lower() in plan_text]
        return {"veto": bool(violations), "violations": violations}
