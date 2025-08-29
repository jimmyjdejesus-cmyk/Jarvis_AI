"""Tests for the MultiTeamOrchestrator graph orchestration."""


class DummyTeam:
    def __init__(self, team, output):
        self.team = team
        self._output = output

    def run(self, objective, context):
        return self._output

    def log(self, *args, **kwargs):
        pass


class DummyOrchestrator:
    def __init__(self):
        self.team_status = {
            t: "running"
            for t in [
                "Red",
                "Blue",
                "Yellow",
                "Green",
                "White",
                "Black",
            ]
        }
        self.log_messages = []
        self.broadcasts = []
        self.teams = {
            "adversary_pair": (
                DummyTeam("Red", {"score": 1}),
                DummyTeam("Blue", {"score": 2}),
            ),
            "competitive_pair": (
                DummyTeam("Yellow", {"score": 1}),
                DummyTeam("Green", {"score": 2}),
            ),
            "security_quality": DummyTeam("White", {"review": "ok"}),
            "innovators_disruptors": DummyTeam(
                "Black", {"innovation": "idea"}
            ),
        }

    def log(self, message, data=None):
        self.log_messages.append(message)

    def broadcast(self, message, data=None):
        self.broadcasts.append((message, data))


def test_multiteam_orchestrator_initialization(multi_team_orchestrator_cls):
    orchestrator = DummyOrchestrator()
    mto = multi_team_orchestrator_cls(orchestrator)
    assert mto.orchestrator is orchestrator
    assert mto.graph is not None


def test_multiteam_orchestrator_state_transitions(multi_team_orchestrator_cls):
    orchestrator = DummyOrchestrator()
    mto = multi_team_orchestrator_cls(orchestrator)
    initial_state = {
        "objective": "test objective",
        "context": {},
        "team_outputs": {},
        "next_team": "competitive_pair",
    }
    final_state = mto.graph.invoke(initial_state)
    assert set(final_state["team_outputs"].keys()) == {
        "competitive_pair",
        "oracle_result",
        "adversary_pair",
        "innovators_disruptors",
        "security_quality",
    }
    assert "reinforced_strategy" in final_state["context"]
    mto.run("test objective")
    assert orchestrator.log_messages[-5:] == [
        "Completed step: competitive_pair",
        "Completed step: adversary_pair",
        "Completed step: innovators_disruptors",
        "Completed step: broadcast_findings",
        "Completed step: security_quality",
    ]
