from dataclasses import dataclass, field
from typing import Dict, List, Any

@dataclass
class CriticInsightMerger:
    def weight_feedback(self, feedback_items):
        return feedback_items

    def synthesize_arguments(self, weighted_feedback):
        max_sev = "low"
        for item in weighted_feedback:
            sev = getattr(item, "severity", "low")
            if sev in ("high", "critical"):
                max_sev = "high"
                break
        return {"combined_argument": "synthesized", "max_severity": max_sev}

@dataclass
class PerformanceTracker:
    metrics: Dict[str, Any] = field(
        default_factory=lambda: {"retry_attempts": 0, "failed_steps": 0}
    )

def record_event(self, event_type: str, success: bool, attempt: int = 1) -> None:
    """Record execution metrics for orchestrator operations."""
    if event_type == "step":
        if not success:
            self.metrics["failed_steps"] += 1
        # A retry is any attempt after the first one, regardless of success.
        if attempt > 1:
            self.metrics["retry_attempts"] += 1
