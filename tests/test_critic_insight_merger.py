import pytest

import config.config_loader as config_loader
from jarvis.monitoring.performance import CriticInsightMerger


def sample_feedback():
    """Provide representative feedback items for testing."""
    return [
        {"text": "minor", "severity": "low", "source_credibility": 0.5},
        {"text": "major", "severity": "high", "source_credibility": 0.8},
        {"text": "crash", "severity": "critical", "source_credibility": 1.0},
    ]


@pytest.mark.parametrize(
    "weights, expected",
    [
        (None, [0.5, 2.4, 4.0]),
        ({"low": 2, "high": 5, "critical": 8}, [1.0, 4.0, 8.0]),
    ],
)
def test_weight_feedback_scores(weights, expected):
    """Weighted scores should reflect severity and credibility."""

    merger = (
        CriticInsightMerger()
        if weights is None
        else CriticInsightMerger(severity_weights=weights)
    )
    weighted = merger.weight_feedback(sample_feedback())
    scores = [item["weighted_score"] for item in weighted]
    assert scores == pytest.approx(expected)


def test_synthesize_arguments_summary():
    """Synthesis should group feedback and report highest severity."""

    merger = CriticInsightMerger()
    weighted = merger.weight_feedback(sample_feedback())
    summary = merger.synthesize_arguments(weighted)

    assert summary["max_severity"] == "critical"
    by_sev = {entry["severity"]: entry for entry in summary["summary"]}
    assert by_sev["high"]["count"] == 1
    assert "crash" in by_sev["critical"]["examples"]


def test_weight_feedback_handles_missing_fields():
    """Items with missing credibility or unknown severity still get scores."""

    merger = CriticInsightMerger()
    feedback = [
        {"text": "odd", "severity": "trivial", "source_credibility": 2},
        {"text": "no cred", "severity": "high"},
        {"text": "no sev", "source_credibility": 0.7},
    ]
    weighted = merger.weight_feedback(feedback)
    scores = [item["weighted_score"] for item in weighted]
    assert scores == pytest.approx([2.0, 3.0, 0.7])

    summary = merger.synthesize_arguments(weighted)
    by_sev = {entry["severity"]: entry for entry in summary["summary"]}
    assert by_sev["trivial"]["count"] == 1


def test_weight_feedback_accepts_objects_without_dict():
    """Slotted objects and namedtuples should be processed correctly."""

    class SlotItem:
        __slots__ = ("severity", "source_credibility")

        def __init__(self, severity, source_credibility):
            self.severity = severity
            self.source_credibility = source_credibility

    from collections import namedtuple

    NT = namedtuple("NT", ["severity", "source_credibility"])

    feedback = [
        SlotItem("low", 0.5),
        NT("high", 0.9),
    ]
    merger = CriticInsightMerger()
    weighted = merger.weight_feedback(feedback)
    scores = [item["weighted_score"] for item in weighted]
    assert scores == pytest.approx([0.5, 2.7])


@pytest.mark.parametrize("cred,fallback", [(0.5, 10), (2.0, 2)])
def test_weight_feedback_configurable_defaults(cred, fallback):
    """Default credibility and fallback weights should be tunable."""

    merger = CriticInsightMerger(
        default_credibility=cred,
        unknown_severity_weight=fallback,
        default_severity="medium",
    )
    feedback = [
        {"text": "mystery", "severity": "other"},
        {"text": "no fields"},
    ]
    weighted = merger.weight_feedback(feedback)

    assert weighted[0]["weighted_score"] == pytest.approx(cred * fallback)
    medium_weight = merger.severity_weights["medium"] * cred
    assert weighted[1]["weighted_score"] == pytest.approx(medium_weight)
    assert weighted[1]["severity"] == "medium"


def test_default_severity_from_config_file(monkeypatch, tmp_path):
    """Merger should honour default severity defined in configuration."""

    monkeypatch.setattr(config_loader, "CONFIG_DIR", tmp_path)
    profiles = tmp_path / "profiles"
    profiles.mkdir()
    monkeypatch.setattr(config_loader, "PROFILES_DIR", profiles)
    (tmp_path / "default.yaml").write_text(
        """
monitoring:
  default_severity: medium
  severity_weights:
    low: 1
    medium: 2
    high: 3
    critical: 4
""",
        encoding="utf-8",
    )
    merger = CriticInsightMerger()
    weighted = merger.weight_feedback([{"text": "no severity"}])
    assert weighted[0]["severity"] == "medium"


def test_default_severity_env_override(monkeypatch):
    """Environment variables should override configuration defaults."""

    monkeypatch.setenv("JARVIS__MONITORING__DEFAULT_SEVERITY", "high")
    merger = CriticInsightMerger()
    weighted = merger.weight_feedback([{"text": "missing"}])
    assert weighted[0]["severity"] == "high"


@pytest.mark.parametrize("limit", [1, 3])
def test_max_examples_from_config(monkeypatch, tmp_path, limit):
    """Example retention should honour ``monitoring.max_examples``."""

    monkeypatch.setattr(config_loader, "CONFIG_DIR", tmp_path)
    profiles = tmp_path / "profiles"
    profiles.mkdir()
    monkeypatch.setattr(config_loader, "PROFILES_DIR", profiles)
    (tmp_path / "default.yaml").write_text(
        f"monitoring:\n  max_examples: {limit}\n", encoding="utf-8"
    )

    feedback = [
        {"text": "l1", "severity": "low"},
        {"text": "l2", "severity": "low"},
        {"text": "h1", "severity": "high"},
        {"text": "h2", "severity": "high"},
        {"text": "h3", "severity": "high"},
    ]
    merger = CriticInsightMerger()
    assert merger.max_examples == limit
    weighted = merger.weight_feedback(feedback)
    summary = merger.synthesize_arguments(weighted)
    by_sev = {entry["severity"]: entry for entry in summary["summary"]}
    assert len(by_sev["low"]["examples"]) == min(2, limit)
    assert len(by_sev["high"]["examples"]) == min(3, limit)


def test_max_examples_and_custom_weights(monkeypatch, tmp_path):
    """Example limits should hold when severity weights are customised."""

    monkeypatch.setattr(config_loader, "CONFIG_DIR", tmp_path)
    profiles = tmp_path / "profiles"
    profiles.mkdir()
    monkeypatch.setattr(config_loader, "PROFILES_DIR", profiles)
    (tmp_path / "default.yaml").write_text(
        """
monitoring:
  max_examples: 1
  severity_weights:
    low: 1
    high: 10
    critical: 5
""",
        encoding="utf-8",
    )

    feedback = [
        {"text": "l1", "severity": "low"},
        {"text": "l2", "severity": "low"},
        {"text": "h1", "severity": "high"},
        {"text": "h2", "severity": "high"},
        {"text": "c1", "severity": "critical"},
    ]

    merger = CriticInsightMerger()
    weighted = merger.weight_feedback(feedback)
    summary = merger.synthesize_arguments(weighted)

    assert summary["max_severity"] == "high"
    by_sev = {entry["severity"]: entry for entry in summary["summary"]}
    assert len(by_sev["low"]["examples"]) == 1
    assert len(by_sev["high"]["examples"]) == 1


def test_max_summary_groups_limit(monkeypatch, tmp_path):
    """Summary group limit should retain only the highest-weight severities."""

    monkeypatch.setattr(config_loader, "CONFIG_DIR", tmp_path)
    profiles = tmp_path / "profiles"
    profiles.mkdir()
    monkeypatch.setattr(config_loader, "PROFILES_DIR", profiles)
    (tmp_path / "default.yaml").write_text(
        "monitoring:\n  max_summary_groups: 2\n", encoding="utf-8"
    )

    feedback = [
        {"text": "l", "severity": "low"},
        {"text": "m", "severity": "medium"},
        {"text": "h", "severity": "high"},
    ]

    merger = CriticInsightMerger()
    weighted = merger.weight_feedback(feedback)
    summary = merger.synthesize_arguments(weighted)

    assert len(summary["summary"]) == 2
    severities = {entry["severity"] for entry in summary["summary"]}
    assert severities == {"high", "medium"}


@pytest.mark.parametrize(
    "weights, limit, cred_high, expected_max",
    [
        ({"low": 1, "high": 10}, 1, 1.0, "high"),
        ({"low": 3, "high": 5}, 2, 0.1, "high"),
    ],
)
def test_weights_examples_and_credibility_interplay(
    weights, limit, cred_high, expected_max
):
    """Weighted scoring should respect credibility and example limits."""

    feedback = [
        {"text": "l1", "severity": "low", "source_credibility": 1.0},
        {"text": "l2", "severity": "low", "source_credibility": 0.5},
        {"text": "h1", "severity": "high", "source_credibility": cred_high},
        {"text": "h2", "severity": "high", "source_credibility": cred_high},
    ]
    merger = CriticInsightMerger(
        severity_weights=weights,
        max_examples=limit,
    )
    weighted = merger.weight_feedback(feedback)
    summary = merger.synthesize_arguments(weighted)

    assert summary["max_severity"] == expected_max
    by_sev = {entry["severity"]: entry for entry in summary["summary"]}
    assert len(by_sev["low"]["examples"]) == min(2, limit)
    assert len(by_sev["high"]["examples"]) == min(2, limit)
    high_scores = [
        i["weighted_score"] for i in weighted if i["severity"] == "high"
    ]
    for score in high_scores:
        assert score == pytest.approx(weights["high"] * cred_high)


def test_summary_score_threshold_filters_low_scoring_groups(
    monkeypatch, tmp_path
):
    """Severity groups below the score threshold should be omitted."""

    monkeypatch.setattr(config_loader, "CONFIG_DIR", tmp_path)
    profiles = tmp_path / "profiles"
    profiles.mkdir()
    monkeypatch.setattr(config_loader, "PROFILES_DIR", profiles)
    (tmp_path / "default.yaml").write_text(
        """
monitoring:
  summary_score_threshold: 5
  severity_weights:
    low: 1
    high: 3
    critical: 4
""",
        encoding="utf-8",
    )

    feedback = [
        {"text": "l", "severity": "low", "source_credibility": 1},
        {"text": "h1", "severity": "high", "source_credibility": 1},
        {"text": "h2", "severity": "high", "source_credibility": 1},
        {"text": "c", "severity": "critical", "source_credibility": 1},
    ]

    merger = CriticInsightMerger()
    weighted = merger.weight_feedback(feedback)
    summary = merger.synthesize_arguments(weighted)

    assert summary["max_severity"] == "critical"
    assert [s["severity"] for s in summary["summary"]] == ["high"]


@pytest.mark.parametrize(
    "cfg_threshold, env_threshold, expected",
    [
        (0, None, ["critical", "high", "low"]),
        (5, None, ["high"]),
        (10, None, []),
        (0, "5", ["high"]),
    ],
)
def test_summary_score_threshold_overrides(
    monkeypatch, tmp_path, cfg_threshold, env_threshold, expected
):
    """Configuration and environment overrides should control score pruning."""

    monkeypatch.setattr(config_loader, "CONFIG_DIR", tmp_path)
    profiles = tmp_path / "profiles"
    profiles.mkdir()
    monkeypatch.setattr(config_loader, "PROFILES_DIR", profiles)
    (tmp_path / "default.yaml").write_text(
        f"""
monitoring:
  summary_score_threshold: {cfg_threshold}
  severity_weights:
    low: 1
    high: 3
    critical: 4
""",
        encoding="utf-8",
    )
    if env_threshold is not None:
        monkeypatch.setenv(
            "JARVIS__MONITORING__SUMMARY_SCORE_THRESHOLD", env_threshold
        )

    feedback = [
        {"text": "l", "severity": "low", "source_credibility": 1},
        {"text": "h1", "severity": "high", "source_credibility": 1},
        {"text": "h2", "severity": "high", "source_credibility": 1},
        {"text": "c", "severity": "critical", "source_credibility": 1},
    ]

    merger = CriticInsightMerger()
    weighted = merger.weight_feedback(feedback)
    summary = merger.synthesize_arguments(weighted)

    assert [s["severity"] for s in summary["summary"]] == expected


@pytest.mark.parametrize(
    "ratio, expected",
    [
        (0, ["critical", "high", "low"]),
        (0.5, ["critical", "high"]),
        (0.75, ["high"]),
    ],
)
def test_summary_score_ratio_filters_groups(
    monkeypatch, tmp_path, ratio, expected
):
    """Dynamic ratio thresholds filter groups relative to the top score."""

    monkeypatch.setattr(config_loader, "CONFIG_DIR", tmp_path)
    profiles = tmp_path / "profiles"
    profiles.mkdir()
    monkeypatch.setattr(config_loader, "PROFILES_DIR", profiles)
    (tmp_path / "default.yaml").write_text(
        f"""
monitoring:
  summary_score_ratio: {ratio}
  severity_weights:
    low: 1
    high: 3
    critical: 4
""",
        encoding="utf-8",
    )

    feedback = [
        {"text": "l", "severity": "low", "source_credibility": 1},
        {"text": "h1", "severity": "high", "source_credibility": 1},
        {"text": "h2", "severity": "high", "source_credibility": 1},
        {"text": "c", "severity": "critical", "source_credibility": 1},
    ]

    merger = CriticInsightMerger()
    weighted = merger.weight_feedback(feedback)
    summary = merger.synthesize_arguments(weighted)

    assert [s["severity"] for s in summary["summary"]] == expected
