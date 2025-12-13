"""Minimal performance tracker shim for tests.

Provides a small in-repo implementation so tests that import
`jarvis.monitoring.performance.PerformanceTracker` succeed
without depending on external monitoring infra.
"""
from __future__ import annotations

from typing import Dict


class PerformanceTracker:
    """Simple tracker that counts failed steps and retry attempts.

    The real project tracker is more sophisticated; this shim implements
    just enough behavior to satisfy unit tests in the integration branch.
    """
    def __init__(self) -> None:
        self.metrics: Dict[str, int] = {
            "failed_steps": 0,
            "retry_attempts": 0,
        }

    def record_event(self, name: str, success: bool, attempt: int = 1) -> None:
        if not success:
            self.metrics["failed_steps"] += 1
        if attempt > 1:
            # Each event with attempt>1 increments retry_attempts by 1
            self.metrics["retry_attempts"] += 1

    def reset(self) -> None:
        self.metrics = {k: 0 for k in self.metrics}
