import os
import types
import sys
import importlib.util
from pathlib import Path

sys.modules.setdefault("langgraph", types.ModuleType("langgraph"))
graph_module = types.ModuleType("langgraph.graph")
graph_module.END = object()
graph_module.StateGraph = type("StateGraph", (), {})
sys.modules["langgraph.graph"] = graph_module

ROOT = Path(__file__).resolve().parents[1]

sys.modules.setdefault("jarvis", types.ModuleType("jarvis"))
sys.modules.setdefault("jarvis.world_model", types.ModuleType("jarvis.world_model"))
sys.modules.setdefault("jarvis.orchestration", types.ModuleType("jarvis.orchestration"))

neo_spec = importlib.util.spec_from_file_location(
    "jarvis.world_model.neo4j_graph", ROOT / "jarvis" / "world_model" / "neo4j_graph.py"
)
neo_module = importlib.util.module_from_spec(neo_spec)
sys.modules["jarvis.world_model.neo4j_graph"] = neo_module
neo_spec.loader.exec_module(neo_module)

mission_spec = importlib.util.spec_from_file_location(
    "jarvis.orchestration.mission", ROOT / "jarvis" / "orchestration" / "mission.py"
)
mission_module = importlib.util.module_from_spec(mission_spec)
sys.modules["jarvis.orchestration.mission"] = mission_module
mission_spec.loader.exec_module(mission_module)

Mission = mission_module.Mission
MissionDAG = mission_module.MissionDAG
MissionNode = mission_module.MissionNode
load_mission = mission_module.load_mission
load_mission_dag_from_neo4j = mission_module.load_mission_dag_from_neo4j
save_mission = mission_module.save_mission
Neo4jGraph = neo_module.Neo4jGraph


class FakeRecord(dict):
    pass


class FakeSession:
    def __init__(self, store):
        self.store = store

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def run(self, query, **params):
        if query.startswith("MERGE (m:Mission"):
            self.store.setdefault("missions", {})[params["mission_id"]] = {
                "rationale": params["rationale"],
            }
            return []
        if query.startswith("MERGE (n:MissionNode"):
            nodes = self.store.setdefault("nodes", {}).setdefault(params["mission_id"], {})
            nodes[params["step_id"]] = {
                "step_id": params["step_id"],
                "capability": params["capability"],
                "team_scope": params["team_scope"],
                "hitl_gate": params["hitl_gate"],
                "deps": params["deps"],
            }
            return []
        if "MERGE (m)-[:HAS_NODE]->(n)" in query:
            return []
        if query.startswith("MATCH (a:MissionNode") and "MERGE (a)-[:DEPENDS_ON]->(b)" in query:
            edges = self.store.setdefault("edges", {}).setdefault(params["mission_id"], [])
            edges.append((params["src"], params["dst"]))
            return []
        if query.startswith(
            "MATCH (m:Mission {id:$mission_id}) RETURN m.rationale AS rationale"
        ):
            mission = self.store.get("missions", {}).get(params["mission_id"], {})
            return [FakeRecord(rationale=mission.get("rationale", ""))]
        if query.startswith(
            "MATCH (n:MissionNode {mission_id:$mission_id}) RETURN"
        ):
            nodes = self.store.get("nodes", {}).get(params["mission_id"], {})
            return [
                FakeRecord(
                    step_id=n["step_id"],
                    capability=n["capability"],
                    team_scope=n["team_scope"],
                    hitl_gate=n["hitl_gate"],
                    deps=n["deps"],
                )
                for n in nodes.values()
            ]
        if query.startswith(
            "MATCH (a:MissionNode {mission_id:$mission_id})-[:DEPENDS_ON]->(b:MissionNode {mission_id:$mission_id}) RETURN"
        ):
            edges = self.store.get("edges", {}).get(params["mission_id"], [])
            return [FakeRecord(src=s, dst=t) for s, t in edges]
        raise NotImplementedError(query)


class FakeDriver:
    def __init__(self):
        self.store = {}

    def session(self):
        return FakeSession(self.store)

    def close(self):
        pass


def test_mission_dag_roundtrip(tmp_path, monkeypatch):
    from jarvis.orchestration import mission as mission_module

    mission_module.MISSION_DIR = tmp_path
    dag = MissionDAG(
        mission_id="m1",
        nodes={
            "a": MissionNode("a", "cap1", "team1"),
            "b": MissionNode("b", "cap2", "team2", deps=["a"]),
        },
        edges=[("a", "b")],
        rationale="test",
    )
    mission = Mission(
        id="m1",
        title="title",
        goal="goal",
        inputs={},
        risk_level="low",
        dag=dag,
    )
    graph = Neo4jGraph(driver=FakeDriver())
    save_mission(mission, graph=graph)
    mission_file = load_mission("m1")
    dag_graph = load_mission_dag_from_neo4j("m1", graph=graph)
    assert mission_file.dag.to_dict() == dag_graph.to_dict()
