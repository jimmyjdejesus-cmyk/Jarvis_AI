import importlib.util
import pathlib
import sys
import types


def load_graph_module():
    root = pathlib.Path(__file__).resolve().parents[1] / "jarvis"
    jarvis_stub = types.ModuleType("jarvis")
    jarvis_stub.__path__ = [str(root)]
    sys.modules.setdefault("jarvis", jarvis_stub)
    orch_stub = types.ModuleType("jarvis.orchestration")
    orch_stub.__path__ = [str(root / "orchestration")]
    sys.modules.setdefault("jarvis.orchestration", orch_stub)

    team_agents_stub = types.ModuleType("jarvis.orchestration.team_agents")

    class OrchestratorAgent:  # pragma: no cover - stub
        pass

    class TeamMemberAgent:  # pragma: no cover - stub
        pass

    team_agents_stub.OrchestratorAgent = OrchestratorAgent
    team_agents_stub.TeamMemberAgent = TeamMemberAgent
    sys.modules.setdefault(
        "jarvis.orchestration.team_agents", team_agents_stub
    )

    pruning_stub = types.ModuleType("jarvis.orchestration.pruning")

    class PruningEvaluator:  # pragma: no cover - stub
        def should_prune(self, *args, **kwargs):
            return False

    pruning_stub.PruningEvaluator = PruningEvaluator
    sys.modules.setdefault("jarvis.orchestration.pruning", pruning_stub)

    critics_stub = types.ModuleType("jarvis.critics")

    class CriticVerdict:  # pragma: no cover - stub
        pass

    class WhiteGate:  # pragma: no cover - stub
        def merge(self, red, blue):
            return CriticVerdict()

    class RedTeamCritic:  # pragma: no cover - stub
        async def review(self, *args, **kwargs):
            return CriticVerdict()

    class BlueTeamCritic:  # pragma: no cover - stub
        async def review(self, *args, **kwargs):
            return CriticVerdict()

    critics_stub.CriticVerdict = CriticVerdict
    critics_stub.WhiteGate = WhiteGate
    critics_stub.RedTeamCritic = RedTeamCritic
    critics_stub.BlueTeamCritic = BlueTeamCritic
    sys.modules.setdefault("jarvis.critics", critics_stub)

    langgraph_stub = types.ModuleType("langgraph.graph")

    class StateGraph:  # pragma: no cover - stub
        def __init__(self, *args, **kwargs):
            pass

        def add_node(self, *args, **kwargs):
            pass

        def set_entry_point(self, *args, **kwargs):
            pass

        def add_edge(self, *args, **kwargs):
            pass

        def compile(self):
            return self

        def stream(self, *_args, **_kwargs):
            return []

    langgraph_stub.StateGraph = StateGraph
    langgraph_stub.END = object()
    sys.modules.setdefault("langgraph.graph", langgraph_stub)
    langgraph_pkg = types.ModuleType("langgraph")
    langgraph_pkg.graph = langgraph_stub
    sys.modules.setdefault("langgraph", langgraph_pkg)

    spec = importlib.util.spec_from_file_location(
        "jarvis.orchestration.graph", root / "orchestration" / "graph.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


graph_module = load_graph_module()
MultiTeamOrchestrator = graph_module.MultiTeamOrchestrator


class DummyGraph:  # pragma: no cover - stub
    def stream(self, *_args, **_kwargs):
        return []


graph_module.MultiTeamOrchestrator._build_graph = (
    lambda self: DummyGraph()
)


class DummyBlackAgent:
    team = "Black"

    def __init__(self):
        self.received_context = None

    def run(self, objective, context):
        self.received_context = context
        return {"status": "ok"}

    def log(self, message, data=None):  # pragma: no cover - noop
        pass


class DummyOrchestrator:
    def __init__(self):
        self.teams = {"innovators_disruptors": DummyBlackAgent()}

    def log(self, *args, **kwargs):  # pragma: no cover - noop
        pass

    def broadcast(self, *args, **kwargs):  # pragma: no cover - noop
        pass


def test_black_team_excludes_white_team_context():
    orchestrator = DummyOrchestrator()
    mto = MultiTeamOrchestrator(orchestrator)
    state = {
        "objective": "test",
        "context": {"foo": "bar", "leak": "secret"},
        "team_outputs": {},
    }

    mto._run_innovators_disruptors(state)

    received = orchestrator.teams["innovators_disruptors"].received_context
    assert "leak" not in received
    assert received["foo"] == "bar"
