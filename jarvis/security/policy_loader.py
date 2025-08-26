"""Load security policies and sanitize prompts."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml


class PolicyLoader:
    """Loader for YAML security policies."""

    def __init__(self, policies_dir: str = "policies") -> None:
        self.policies_dir = Path(policies_dir)

    def load_policies(self) -> Dict[str, Dict[str, Any]]:
        """Load all YAML policies from the directory."""
        policies: Dict[str, Dict[str, Any]] = {}
        if not self.policies_dir.exists():
            return policies
        for path in self.policies_dir.glob("*.yml"):
            with path.open("r", encoding="utf-8") as f:
                policies[path.stem] = yaml.safe_load(f) or {}
        for path in self.policies_dir.glob("*.yaml"):
            with path.open("r", encoding="utf-8") as f:
                policies[path.stem] = yaml.safe_load(f) or {}
        return policies

    def _blocked_phrases(self, policies: Dict[str, Dict[str, Any]]) -> List[str]:
        phrases: List[str] = []
        for policy in policies.values():
            phrases.extend(policy.get("blocked_phrases", []))
        return phrases

    def sanitize_prompt(self, prompt: str) -> str:
        policies = self.load_policies()
        sanitized = prompt
        for phrase in self._blocked_phrases(policies):
            sanitized = sanitized.replace(phrase, "[REDACTED]")
        return sanitized

    def is_prompt_allowed(self, prompt: str) -> bool:
        policies = self.load_policies()
        lowered = prompt.lower()
        return not any(phrase.lower() in lowered for phrase in self._blocked_phrases(policies))
