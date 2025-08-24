"""Risk annotation for tool executions with HITL approval hooks."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

class ActionRequestApproval(Exception):
    """Raised when a tool requires human approval before execution."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

@dataclass
class RiskAnnotator:
    """Very small risk evaluator for tools.

    The annotator checks provided tool metadata and returns a risk level
    ("low", "medium", or "high"). High risk emits ``ActionRequestApproval``
    which upstream components can catch to pause execution and seek
    confirmation.
    """

    def evaluate(self, tool: str, metadata: Dict[str, Any]) -> str:
        """Evaluate risk for ``tool`` given ``metadata``."""
        level = metadata.get("risk", "low").lower()
        if level == "high":
            raise ActionRequestApproval(f"Approval required for {tool}")
        return level
