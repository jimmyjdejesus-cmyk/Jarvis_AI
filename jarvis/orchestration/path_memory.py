from __future__ import annotations
from typing import Any, List


class PathMemory:
    """A simple path memory store used by the orchestrator during tests.

    The production PathMemory is more complex, but the tests only require
    adding decisions and possibly reading them back.
    """
    def __init__(self) -> None:
        self.decisions: List[Any] = []
        self.steps: List[Any] = []
        self.records: List[Any] = []

    def add_decisions(self, decisions: List[Any]) -> None:
        if decisions:
            self.decisions.extend(decisions)

    def add_step(self, step: Any) -> None:
        self.steps.append(step)

    def should_avoid(self) -> tuple[bool, float]:
        """Return whether the current path should be avoided and a similarity metric.

        A minimal implementation always returns (False, 0.0) so the orchestrator can
        proceed; more advanced heuristics may be added in a later refactor.
        """
        return False, 0.0

    def get_decisions(self) -> List[Any]:
        return list(self.decisions)

    def get_steps(self) -> List[Any]:
        return list(self.steps)

    def record(self, score: float) -> None:
        """Record the final score for this path."""
        self.records.append(score)

    def get_records(self) -> List[Any]:
        return list(self.records)
