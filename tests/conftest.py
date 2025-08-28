@pytest.fixture
def mock_neo4j_graph(monkeypatch):
    """Provide a mock Neo4j graph for tests."""

    mock_graph = MagicMock()
    mock_graph.connect = MagicMock()
    mock_graph.close = MagicMock()
    mock_graph.run = MagicMock(return_value=MagicMock(data=MagicMock(return_value=[])))

    monkeypatch.setattr(
        "jarvis.world_model.neo4j_graph.Neo4jGraph", MagicMock(return_value=mock_graph)
    )
    yield mock_graph


def load_graph_module(monkeypatch):
    """Load `jarvis.orchestration.graph` with isolated stubs."""
    root = Path(__file__).resolve().parents[1] / "jarvis"

    # Provide fresh langgraph/networkx stubs per invocation
    langgraph_graph = types.ModuleType("langgraph.graph")
    langgraph_graph.END = object()

    class StateGraph:  # pragma: no cover - minimal stub
        def __init__(self, *args, **kwargs):
            self.nodes = {}
            self.edges = {}
            self.entry = None

        def add_node(self, name, fn):
            self.nodes[name] = fn

        def set_entry_point(self, name):
            self.entry = name

        def add_edge(self, src, dst):
            self.edges[src] = dst

        def compile(self):
            nodes = self.nodes
            edges = self.edges
            entry = self.entry

            class _CompiledGraph:
                def stream(self, state):
                    current = entry
                    while current:
                        fn = nodes[current]
                        state = fn(state)
                        yield {current: state}
                        if state.get("halt"):
                            break
                        nxt = edges.get(current)
                        if nxt is langgraph_graph.END:
                            break
                        current = nxt

            return _CompiledGraph()

    langgraph_graph.StateGraph = StateGraph
    langgraph_module = types.ModuleType("langgraph")
    langgraph_module.graph = langgraph_graph
    monkeypatch.setitem(sys.modules, "langgraph", langgraph_module)
    monkeypatch.setitem(sys.modules, "langgraph.graph", langgraph_graph)
    monkeypatch.setitem(sys.modules, "networkx", types.ModuleType("networkx"))

    jarvis_stub = types.ModuleType("jarvis")
    jarvis_stub.__path__ = [str(root)]
    monkeypatch.setitem(sys.modules, "jarvis", jarvis_stub)

    orch_stub = types.ModuleType("jarvis.orchestration")
    orch_stub.__path__ = [str(root / "orchestration")]
    monkeypatch.setitem(sys.modules, "jarvis.orchestration", orch_stub)

    team_agents_stub = types.ModuleType("jarvis.orchestration.team_agents")

    class OrchestratorAgent:  # pragma: no cover - stub
        pass

    class TeamMemberAgent:  # pragma: no cover - stub
        pass

    team_agents_stub.OrchestratorAgent = OrchestratorAgent
    team_agents_stub.TeamMemberAgent = TeamMemberAgent
    monkeypatch.setitem(
        sys.modules, "jarvis.orchestration.team_agents", team_agents_stub
    )

    pruning_stub = types.ModuleType("jarvis.orchestration.pruning")

    class PruningEvaluator:  # pragma: no cover - stub
        def should_prune(self, *args, **kwargs):
            return False

        async def evaluate(self, *args, **kwargs):  # pragma: no cover - stub
            pass