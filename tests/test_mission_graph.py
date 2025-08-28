from jarvis.agents.mission_planner import MissionPlanner
from jarvis.orchestration.mission import update_node_state, get_mission_graph
from jarvis.world_model.knowledge_graph import KnowledgeGraph


class _Memory:
    def query(self, project: str, session: str, goal: str):
        return [{"hit": 1}]


def test_plan_updates_graph_and_retrieval():
    kg = KnowledgeGraph()
    planner = MissionPlanner(memory=_Memory(), knowledge_graph=kg)
    dag = planner.plan("do thing", {"title": "t"})

    assert "memory_recall" in kg.graph
    assert kg.graph.nodes["memory_recall"]["mission_id"] == dag.mission_id

    update_node_state(dag.mission_id, "memory_recall", "succeeded", graph=kg)
    assert kg.graph.nodes["memory_recall"]["status"] == "succeeded"

    mission_graph = get_mission_graph(dag.mission_id, kg)
    node_ids = [n for n, _ in mission_graph["nodes"]]
    assert "memory_recall" in node_ids
    edge_pairs = [(s, t) for s, t, _ in mission_graph["edges"]]
    assert ("memory_recall", "execute_goal") in edge_pairs
