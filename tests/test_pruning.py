import sys
from pathlib import Path
import types

import pytest

# Ensure repository root is on path for direct module imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

sys.modules.setdefault("networkx", types.SimpleNamespace())
dummy_neo4j = types.SimpleNamespace(GraphDatabase=object, Driver=object)
sys.modules.setdefault("neo4j", dummy_neo4j)

from jarvis.orchestration.message_bus import MessageBus
from jarvis.orchestration.pruning import PruningEvaluator
from memory_service import _paths, Metrics, Outcome, PathSignature


@pytest.mark.asyncio
async def test_prune_suggestion_emitted():
    bus = MessageBus()
    evaluator = PruningEvaluator(bus)
    events = []

    async def handler(event):
        events.append(event)

    bus.subscribe("orchestrator.prune_suggested", handler)

    # First output establishes history
    await evaluator.evaluate("team1", {"text": "hello world", "quality": 0.5, "cost": 1})
    # Second output is identical -> low novelty and zero growth triggers prune
    await evaluator.evaluate("team1", {"text": "hello world", "quality": 0.5, "cost": 1})

    assert events, "prune event should be emitted when thresholds not met"
    payload = events[0]["payload"]
    assert payload["team_id"] == "team1"
    scores = payload["scores"]
    assert scores["novelty"] == 0


@pytest.mark.asyncio
async def test_merge_and_dead_end_events():
    bus = MessageBus()
    evaluator = PruningEvaluator(bus)
    merge_events = []
    dead_events = []

    bus.subscribe("orchestrator.team_merged", lambda e: merge_events.append(e))
    bus.subscribe("orchestrator.path_dead_end", lambda e: dead_events.append(e))

    _paths.clear()

    sig = PathSignature(
        steps=["s"],
        tools_used=["s"],
        key_decisions=[],
        embedding=[],
        metrics=Metrics(novelty=0.0, growth=0.0, cost=0.0),
        outcome=Outcome(result="fail", oracle_score=0.0),
        scope="project",
    )
    await evaluator.merge_state("t1", "t2", ["a.txt"], signature=sig)
    await evaluator.mark_dead_end("t1", sig)

    assert merge_events and dead_events
    assert merge_events[0]["payload"]["from_team"] == "t1"
    assert dead_events[0]["payload"]["team_id"] == "t1"
    assert _paths["project"]["negative"]
