import types
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List


def load_executive_agent():
    jarvis = types.ModuleType("jarvis")
    sys.modules.setdefault("jarvis", jarvis)

    def ensure(name: str):
        mod = types.ModuleType(name)
        sys.modules[name] = mod
        return mod

    # Minimal stubs for imports required by meta_intelligence
    ensure("jarvis.agents.agent_resources").AgentCapability = type("AgentCapability", (), {})
    sys.modules["jarvis.agents.agent_resources"].AgentMetrics = type("AgentMetrics", (), {})
    sys.modules["jarvis.agents.agent_resources"].SystemEvolutionPlan = type("SystemEvolutionPlan", (), {})
    sys.modules["jarvis.agents.agent_resources"].SystemHealth = type("SystemHealth", (), {})

    ensure("jarvis.agents.base").AIAgent = type("AIAgent", (), {})

    critics = ensure("jarvis.agents.critics")
    class CriticVerdict:
        def __init__(self, approved=True, fixes=None, score=0.0, notes=""):
            self.approved = approved
            self.fixes = fixes or []
            self.score = score
            self.notes = notes
        def to_dict(self):
            return {}
    critics.CriticVerdict = CriticVerdict
    critics.BlueTeamCritic = type("BlueTeamCritic", (), {})
    critics.ConstitutionalCritic = type("ConstitutionalCritic", (), {})
    critics.CriticFeedback = type("CriticFeedback", (), {})
    critics.RedTeamCritic = type("RedTeamCritic", (), {})
    class WhiteGate:
        def merge(self, *_args, **_kwargs):
            return CriticVerdict()
    critics.WhiteGate = WhiteGate

    ensure("jarvis.agents.curiosity_agent").CuriosityAgent = type("CuriosityAgent", (), {"generate_question": lambda self: None})
    ensure("jarvis.agents.mission_planner").MissionPlanner = type("MissionPlanner", (), {"plan": lambda self, d, c: None, "to_graph": lambda self, t: {}})
    ensure("jarvis.agents.specialist").SpecialistAgent = type("SpecialistAgent", (), {})

    mem_mod = ensure("jarvis.memory.project_memory")
    class MemoryManager: ...
    class ProjectMemory(MemoryManager): ...
    mem_mod.MemoryManager = MemoryManager
    mem_mod.ProjectMemory = ProjectMemory

    perf_mod = ensure("jarvis.monitoring.performance")
    perf_mod.CriticInsightMerger = type("CriticInsightMerger", (), {})
    perf_mod.PerformanceTracker = type("PerformanceTracker", (), {})

    ensure("jarvis.homeostasis").SystemMonitor = type("SystemMonitor", (), {})

    orch_mod = ensure("jarvis.orchestration.orchestrator")
    orch_mod.AgentSpec = type("AgentSpec", (), {})
    orch_mod.DynamicOrchestrator = type("DynamicOrchestrator", (), {})
    orch_mod.MultiAgentOrchestrator = type("MultiAgentOrchestrator", (), {})

    ensure("jarvis.orchestration.sub_orchestrator").SubOrchestrator = type("SubOrchestrator", (), {})
    ensure("jarvis.persistence.session").SessionManager = type("SessionManager", (), {})
    ensure("jarvis.world_model.knowledge_graph").KnowledgeGraph = type("KnowledgeGraph", (), {})
    ensure("jarvis.world_model.hypergraph").HierarchicalHypergraph = type("HierarchicalHypergraph", (), {})

    neo_mod = ensure("jarvis.world_model.neo4j_graph")
    class Neo4jGraph:
        def add_node(self, *_a, **_k): ...
        def add_edge(self, *_a, **_k): ...
        def close(self): ...
    neo_mod.Neo4jGraph = Neo4jGraph

    mission_mod = ensure("jarvis.orchestration.mission")
    @dataclass
    class MissionNode:
        step_id: str
        capability: str = ""
        team_scope: str = ""
        hitl_gate: bool = False
        deps: List[str] = field(default_factory=list)
    @dataclass
    class MissionDAG:
        mission_id: str
        nodes: Dict[str, MissionNode] = field(default_factory=dict)
        edges: List[tuple[str, str]] = field(default_factory=list)
        rationale: str = ""
    @dataclass
    class Mission:
        id: str
        title: str
        goal: str
        inputs: Dict[str, object]
        risk_level: str
        dag: MissionDAG
    mission_mod.Mission = Mission
    mission_mod.MissionDAG = MissionDAG
    mission_mod.MissionNode = MissionNode

    code = Path("jarvis/ecosystem/meta_intelligence.py").read_text()
    code = code.split("class MetaIntelligenceCore")[0]
    module = types.ModuleType("meta_intelligence_partial")
    exec(code, module.__dict__)
    return module.ExecutiveAgent, Mission, MissionDAG, MissionNode


ExecutiveAgent, Mission, MissionDAG, MissionNode = load_executive_agent()


class DummyGraph:
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.closed = False
    def add_node(self, node_id, node_type, attributes=None):
        self.nodes.append((node_id, node_type, attributes))
    def add_edge(self, source, target, rel_type, attributes=None):
        self.edges.append((source, target, rel_type, attributes))
    def close(self):
        self.closed = True


def test_update_world_model_records_nodes_and_edges():
    agent = object.__new__(ExecutiveAgent)
    agent.neo4j_graph = DummyGraph()

    mission = Mission(
        id="m1",
        title="",
        goal="goal",
        inputs={},
        risk_level="low",
        dag=MissionDAG(mission_id="m1", rationale="plan"),
    )
    mission.dag.nodes["s1"] = MissionNode(step_id="s1", capability="cap", team_scope="team")

    results = [
        {
            "step_id": "s1",
            "success": True,
            "facts": [{"id": "f1", "type": "fact", "attributes": {"k": "v"}}],
            "relationships": [{"source": "f1", "target": "s1", "type": "REL"}],
        }
    ]

    agent._update_world_model(mission, results)
    graph = agent.neo4j_graph

    assert ("m1", "mission", {"goal": "goal", "rationale": "plan"}) in graph.nodes
    assert ("s1", "step", {"capability": "cap", "team_scope": "team"}) in graph.nodes
    assert ("s1", "step", {"status": "COMPLETED"}) in graph.nodes
    assert ("f1", "fact", {"k": "v"}) in graph.nodes

    assert ("m1", "s1", "HAS_STEP", None) in graph.edges
    assert ("m1", "s1", "COMPLETED", None) in graph.edges
    assert ("s1", "f1", "DISCOVERED", None) in graph.edges
    assert ("f1", "s1", "REL", None) in graph.edges
    assert not graph.closed
