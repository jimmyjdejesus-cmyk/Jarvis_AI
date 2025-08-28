"""Simple performance tracking utilities used in tests."""

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional

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
    except (OSError, TypeError, ValueError):
        pass
    return defaults


def _default_severity() -> str:
    """Retrieve the default severity level for feedback items."""

    try:  # pragma: no cover - defensive
        cfg = load_config()
        value = cfg.get("monitoring", {}).get("default_severity", "low")
        return str(value)
    except (OSError, TypeError, ValueError):
        return "low"


def _default_credibility() -> float:
    """Retrieve the default credibility multiplier from configuration."""

    try:  # pragma: no cover - defensive
        cfg = load_config()
        value = cfg.get("monitoring", {}).get("default_credibility", 1.0)
        return float(value)
    except (TypeError, ValueError):
        return 1.0


def _unknown_severity_weight() -> int:
    """Weight applied when a severity value is unrecognised."""

    try:  # pragma: no cover - defensive
        cfg = load_config()
        value = cfg.get("monitoring", {}).get("unknown_severity_weight", 1)
        return int(value)
    except (OSError, TypeError, ValueError):
        return 1


def _max_examples() -> int:
    """Retrieve the example limit for synthesized summaries.

    Reads ``monitoring.max_examples`` from configuration and falls back to
    ``2`` when unspecified or invalid.
    """

    try:  # pragma: no cover - defensive
        cfg = load_config()
        value = cfg.get("monitoring", {}).get("max_examples", 2)
        return int(value)
    except (OSError, TypeError, ValueError):
        return 2


def _max_summary_groups() -> Optional[int]:
    """Retrieve the summary group limit for synthesized arguments.

    Reads ``monitoring.max_summary_groups`` from configuration and returns
    ``None`` when the value is missing or invalid, which preserves all
    severity groups.
    """

    try:  # pragma: no cover - defensive
        cfg = load_config()
        value = cfg.get("monitoring", {}).get("max_summary_groups")
        if value is None:
            return None
        return int(value)
    except (OSError, TypeError, ValueError):
        return None


def _summary_score_threshold() -> Optional[float]:
    """Retrieve the score threshold for summary inclusion.

    Reads ``monitoring.summary_score_threshold`` from configuration and returns
    ``None`` when the value is missing or invalid, which allows all severity
    groups to appear regardless of aggregated score.
    """

    try:  # pragma: no cover - defensive
        cfg = load_config()
        value = cfg.get("monitoring", {}).get("summary_score_threshold")
        if value is None:
            return None
        return float(value)
    except (OSError, TypeError, ValueError):
        return None


def _summary_score_ratio() -> Optional[float]:
    """Retrieve the score ratio for dynamic summary filtering.

    Reads ``monitoring.summary_score_ratio`` from configuration and returns
    ``None`` when the value is missing or invalid. When configured, the ratio
    is multiplied by the highest aggregated severity score to derive a dynamic
    threshold.
    """

    try:  # pragma: no cover - defensive
        cfg = load_config()
        value = cfg.get("monitoring", {}).get("summary_score_ratio")
        if value is None:
            return None
        return float(value)
    except (OSError, TypeError, ValueError):
        return None


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
    in the global configuration and may be overridden via constructor. The
    number of example feedback items retained per severity is controlled by
    ``monitoring.max_examples``. The total number of severity groups emitted in
    the synthesized summary can be constrained via
    ``monitoring.max_summary_groups``. Severity groups whose aggregated score
    falls below ``monitoring.summary_score_threshold`` or below a dynamic
    ``monitoring.summary_score_ratio`` of the highest-scoring group may be
    omitted entirely from the synthesized summary.
    """

    #: Weights applied to each severity level, loaded from configuration.
    severity_weights: Dict[str, int] = field(
        default_factory=_default_severity_weights
    )
    #: Severity applied when feedback omits the field.
    default_severity: str = field(default_factory=_default_severity)
    #: Credibility used when feedback omits the field.
    default_credibility: float = field(default_factory=_default_credibility)
    #: Weight applied to unknown severity values.
    unknown_severity_weight: int = field(
        default_factory=_unknown_severity_weight
    )
    #: Maximum number of examples retained for each severity group.
    max_examples: int = field(default_factory=_max_examples)
    #: Maximum number of severity groups included in summaries.
    max_summary_groups: Optional[int] = field(
        default_factory=_max_summary_groups
    )
    #: Minimum aggregated score required for a severity group to appear
    #: in summaries.
    summary_score_threshold: Optional[float] = field(
        default_factory=_summary_score_threshold
    )
    #: Minimum ratio of the top severity score required for a group to appear.
    summary_score_ratio: Optional[float] = field(
        default_factory=_summary_score_ratio
    )

    def _as_dict(self, item: Any) -> Dict[str, Any]:  # pragma: no cover
        """Return a dictionary representation of ``item``.

        Objects without a ``__dict__`` (e.g. those using ``__slots__`` or
        namedtuples) are supported by falling back to ``getattr``.
        """

        if isinstance(item, dict):
            return item.copy()
        try:
            return vars(item).copy()
        except TypeError:
            data: Dict[str, Any] = {}
            for attr in dir(item):
                if attr.startswith("_"):
                    continue
                try:
                    value = getattr(item, attr)
                except AttributeError:
                    continue
                if not callable(value):
                    data[attr] = value
            return data

    def weight_feedback(
        self, feedback_items: Iterable[Any]
    ) -> List[Dict[str, Any]]:
        """Attach a weighted score to each feedback entry.

        The score is calculated as ``severity_weight * source_credibility``.
        Severity defaults to a configurable value when missing, and
        credibility falls back to a configurable multiplier.
        """

        weighted: List[Dict[str, Any]] = []
        for fb in feedback_items:
            data = self._as_dict(fb)
            sev = data.get("severity", self.default_severity)
            data.setdefault("severity", sev)
            try:
                cred = float(
                    data.get("source_credibility", self.default_credibility)
                )
            except (TypeError, ValueError):
                cred = self.default_credibility
            score = self.severity_weights.get(
                sev, self.unknown_severity_weight
            ) * cred
            data["weighted_score"] = score
            weighted.append(data)
        return weighted

    def synthesize_arguments(
        self, weighted_feedback: Iterable[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create a structured summary with examples from weighted feedback.

        The number of feedback examples preserved for each severity group is
        limited by ``max_examples``. Severity groups with a total weighted
        score below ``summary_score_threshold`` or below the highest score
        multiplied by ``summary_score_ratio`` are excluded when the respective
        thresholds are configured.
        """

        grouped: Dict[str, List[Dict[str, Any]]] = {}
        scores: Dict[str, float] = {}
        max_sev = self.default_severity
        max_weight = self.severity_weights.get(self.default_severity, 1)

        for item in weighted_feedback:
            sev = item.get("severity", self.default_severity)
            grouped.setdefault(sev, []).append(item)
            scores[sev] = scores.get(sev, 0.0) + float(
                item.get("weighted_score", 0.0)
            )
            weight = self.severity_weights.get(sev, 1)
            if weight > max_weight:
                max_weight = weight
                max_sev = sev

        top_score = max(scores.values(), default=0.0)
        ratio_threshold = (
            top_score * self.summary_score_ratio
            if self.summary_score_ratio is not None
            else None
        )

        summary = []
        for sev, items in grouped.items():
            total = scores.get(sev, 0.0)
            if (
                self.summary_score_threshold is not None
                and total < self.summary_score_threshold
            ) or (
                ratio_threshold is not None and total < ratio_threshold
            ):
                continue
            summary.append(
                {
                    "severity": sev,
                    "count": len(items),
                    "examples": [
                        i.get("text") or i.get("message")
                        for i in items[: self.max_examples]
                    ],
                }
            )

        summary.sort(
            key=lambda e: self.severity_weights.get(e["severity"], 0),
            reverse=True,
        )
        if self.max_summary_groups is not None:
            summary = summary[: self.max_summary_groups]

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
