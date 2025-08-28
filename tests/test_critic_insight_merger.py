import pytest
from jarvis.monitoring.performance import CriticInsightMerger


def sample_feedback():
    """Provide representative feedback items for testing."""
    return [
        {"text": "minor", "severity": "low", "source_credibility": 0.5},
        {"text": "major", "severity": "high", "source_credibility": 0.8},
        {"text": "crash", "severity": "critical", "source_credibility": 1.0},
    ]


def test_weight_feedback_scores():
    """Weighted scores should reflect severity and credibility."""

    merger = CriticInsightMerger()
    weighted = merger.weight_feedback(sample_feedback())
    scores = [item["weighted_score"] for item in weighted]
    assert scores == pytest.approx([0.5, 2.4, 4.0])


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
