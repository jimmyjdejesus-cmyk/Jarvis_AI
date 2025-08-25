import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jarvis.orchestration.pruning import PruningEvaluator
from jarvis.orchestration.message_bus import MessageBus
from jarvis.orchestration.graph import MultiTeamOrchestrator


class DummyTeam:
    def __init__(self, name):
        self.team = name

    def run(self, objective, context):
        return {"text": "hello", "quality": 0.5, "cost": 1.0}


class DummyOrchestrator:
    def __init__(self):
        dummy = DummyTeam("Dummy")
        self.teams = {
            "adversary_pair": (dummy, dummy),
            "competitive_pair": (dummy, dummy),
            "security_quality": dummy,
            "innovators_disruptors": dummy,
        }

    def broadcast(self, *args, **kwargs):
        pass

    def log(self, *args, **kwargs):
        pass


def test_pruning_event_emitted():
    bus = MessageBus()
    evaluator = PruningEvaluator(bus)
    orch = DummyOrchestrator()
    mto = MultiTeamOrchestrator(orch, evaluator=evaluator)
    events = []
    bus.subscribe("orchestrator.prune_suggested", lambda e: events.append(e))
    state = {"objective": "obj", "context": {}, "team_outputs": {}}
    # Run same team twice to trigger low novelty
    mto._run_team(orch.teams["security_quality"], state)
    mto._run_team(orch.teams["security_quality"], state)
    assert events, "Prune event should be emitted on repeated outputs"


def test_pruned_team_skipped():
    bus = MessageBus()
    evaluator = PruningEvaluator(bus)
    orch = DummyOrchestrator()
    mto = MultiTeamOrchestrator(orch, evaluator=evaluator)
    state = {"objective": "obj", "context": {}, "team_outputs": {}}
    team = orch.teams["security_quality"]
    mto._run_team(team, state)
    mto._run_team(team, state)  # second run triggers prune suggestion
    result = mto._run_team(team, state)
    assert result == {"status": "pruned"}
