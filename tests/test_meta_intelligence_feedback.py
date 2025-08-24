import pytest

from jarvis.ecosystem.meta_intelligence import (
    CriticFeedback,
    CriticInsightMerger,
    MetaIntelligenceCore,
)
def test_feedback_weighting_and_synthesis():
    merger = CriticInsightMerger()
    feedbacks = [
        CriticFeedback(critic_id="c1", message="Issue A", severity="high", confidence=0.9),
        CriticFeedback(critic_id="c2", message="Issue B", severity="low", confidence=0.5),
    ]
    weighted = merger.weight_feedback(feedbacks)
    assert weighted[0].weight >= weighted[1].weight
    synthesis = merger.synthesize_arguments(weighted)
    assert "Issue A" in synthesis["combined_argument"]
    assert synthesis["max_severity"] == "high"


@pytest.mark.asyncio
async def test_adaptive_retry_strategy():
    core = MetaIntelligenceCore()
    attempts = {"count": 0}

    async def failing_once():
        attempts["count"] += 1
        if attempts["count"] < 2:
            raise ValueError("fail")
        return "ok"

    result = await core._adaptive_retry(failing_once, severity="high")
    assert result == "ok"
    assert attempts["count"] == 2
