"""Simple performance tracking utilities used in tests."""

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List

from config.config_loader import load_config


def _default_severity_weights() -> Dict[str, int]:
    """Load severity weights from configuration.

    Falls back to built-in defaults when no configuration is present or if
    any values are invalid.
    """

    defaults: Dict[str, int] = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4,
    }
    try:  # pragma: no cover - defensive; config loader already tested
        cfg = load_config()
        weights = cfg.get("monitoring", {}).get("severity_weights", {})
        if isinstance(weights, dict):
            for key, value in weights.items():
                try:
                    defaults[key] = int(value)
                except (TypeError, ValueError):
                    continue
    except Exception:
        pass
    return defaults


@dataclass
class CriticInsightMerger:
    """Merge critic feedback into weighted arguments.

    This class is intentionally lightweight and is primarily used in tests to
    provide deterministic behaviour. Feedback items are expected to expose at
    least ``severity`` and ``source_credibility`` fields (either as
    attributes or dictionary keys). ``weight_feedback`` calculates a
    numeric score for each item and ``synthesize_arguments`` groups
    items by severity while also determining the highest severity
    present. Severity weights are loaded from ``monitoring.severity_weights``
    in the global configuration and may be overridden via constructor.
    """

    #: Weights applied to each severity level, loaded from configuration.
    severity_weights: Dict[str, int] = field(
        default_factory=_default_severity_weights
    )

    def _as_dict(self, item: Any) -> Dict[str, Any]:  # pragma: no cover
        """Return a dictionary representation of ``item``."""

        return item if isinstance(item, dict) else item.__dict__.copy()

    def weight_feedback(
        self, feedback_items: Iterable[Any]
    ) -> List[Dict[str, Any]]:
        """Attach a weighted score to each feedback entry.

        The score is calculated as ``severity_weight * source_credibility``.
        Both fields default to ``"low"`` severity and a credibility of ``1.0``
        when missing.
        """

        weighted: List[Dict[str, Any]] = []
        for fb in feedback_items:
            data = self._as_dict(fb)
            sev = data.get("severity", "low")
            try:
                cred = float(data.get("source_credibility", 1.0))
            except (TypeError, ValueError):
                cred = 1.0
            score = self.severity_weights.get(sev, 1) * cred
            data["weighted_score"] = score
            weighted.append(data)
        return weighted

    def synthesize_arguments(
        self, weighted_feedback: Iterable[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create a structured summary with examples from weighted feedback."""

        grouped: Dict[str, List[Dict[str, Any]]] = {}
        max_sev = "low"
        max_weight = 0

        for item in weighted_feedback:
            sev = item.get("severity", "low")
            grouped.setdefault(sev, []).append(item)
            weight = self.severity_weights.get(sev, 1)
            if weight > max_weight:
                max_weight = weight
                max_sev = sev

        summary = [
            {
                "severity": sev,
                "count": len(items),
                "examples": [
                    i.get("text") or i.get("message") for i in items[:2]
                ],
            }
            for sev, items in grouped.items()
        ]

        return {"summary": summary, "max_severity": max_sev}


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
            if attempt > 1:
                self.metrics["retry_attempts"] += 1
