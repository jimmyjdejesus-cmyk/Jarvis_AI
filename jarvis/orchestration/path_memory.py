"""Path memory integration for orchestrator."""
from __future__ import annotations

from typing import List

from memory_service import (
    Metrics,
    NegativeCheck,
    Outcome,
    PathRecord,
    PathSignature,
    avoid_negative,
    record_path,
)


class PathMemory:
    """Track and persist reasoning paths through the memory service."""

    def __init__(self, actor: str = "orchestrator", target: str = "project") -> None:
        self.actor = actor
        self.target = target
        self.steps: List[str] = []
        self.tools: List[str] = []
        self.decisions: List[str] = []

    # ------------------------------------------------------------------
    def add_step(self, step: str) -> None:
        """Record an execution step.

        Parameters
        ----------
        step:
            Identifier for the step or specialist involved.
        """
        self.steps.append(step)
        if step not in self.tools:
            # Treat specialists as tools for signature purposes
            self.tools.append(step)

    def add_decisions(self, decisions: List[str]) -> None:
        """Append key decisions gathered during execution."""
        self.decisions.extend(decisions)

    # ------------------------------------------------------------------
    def should_avoid(self, threshold: float = 0.8) -> bool:
        """Check negative path memory to determine if execution should be avoided."""
        signature = PathSignature(
            steps=self.steps,
            tools_used=self.tools,
            key_decisions=self.decisions,
            metrics=Metrics(novelty=0.0, growth=0.0, cost=0.0),
            outcome=Outcome(result="fail"),
            scope=self.target,
        )
        result = avoid_negative(
            NegativeCheck(
                actor=self.actor, target=self.target, signature=signature, threshold=threshold
            )
        )
        return bool(result.get("avoid"))

    # ------------------------------------------------------------------
    def record(self, success: bool) -> None:
        """Persist the current path signature to the memory service."""
        novelty = len(set(self.steps)) / max(len(self.steps), 1)
        growth = len(set(self.decisions)) / max(len(self.decisions), 1) if self.decisions else 0.0
        cost = float(len(self.tools))

        signature = PathSignature(
            steps=self.steps,
            tools_used=self.tools,
            key_decisions=self.decisions,
            metrics=Metrics(novelty=novelty, growth=growth, cost=cost),
            outcome=Outcome(result="pass" if success else "fail"),
            scope=self.target,
        )
        record_path(
            PathRecord(
                actor=self.actor,
                target=self.target,
                kind="positive" if success else "negative",
                signature=signature,
            )
        )
