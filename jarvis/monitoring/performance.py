from dataclasses import dataclass, field
from typing import Dict, List, Any

@dataclass
class CriticInsightMerger:
    def weight_feedback(self, feedback_items):
        return feedback_items
    def synthesize_arguments(self, weighted_feedback):
        return {"combined_argument": "synthesized", "max_severity": "low"}

@dataclass
class PerformanceTracker:
    metrics: Dict[str, Any] = field(default_factory=dict)
    def record_event(self, event_type: str, success: bool, attempt: int = 1):
        if "retry_attempts" not in self.metrics:
            self.metrics["retry_attempts"] = 0
        if success:
            pass
        else:
            self.metrics["retry_attempts"] +=1
