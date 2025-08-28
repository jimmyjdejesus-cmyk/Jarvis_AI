"""Simple performance tracking utilities used in tests."""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class CriticInsightMerger:
    """Placeholder merger that returns basic aggregate information."""

    def weight_feedback(self, feedback_items):  # pragma: no cover - trivial
        return feedback_items

    def synthesize_arguments(
        self, weighted_feedback
    ):  # pragma: no cover - trivial
        max_sev = "low"
        for item in weighted_feedback:
            sev = getattr(item, "severity", "low")
            if sev in ("high", "critical"):
                max_sev = "high"
                break
        return {"combined_argument": "synthesized", "max_severity": max_sev}


@dataclass
class PerformanceTracker:
    """Record execution metrics for orchestrator operations."""

    metrics: Dict[str, Any] = field(
        default_factory=lambda: {"retry_attempts": 0, "failed_steps": 0}
    )

    def record_event(
        self, event_type: str, success: bool, attempt: int = 1
    ) -> None:
        if event_type == "step":
            if not success:
                self.metrics["failed_steps"] += 1
            # Count any attempt after the first as a retry,
            # regardless of success.
            if attempt > 1:
                self.metrics["retry_attempts"] += 1
