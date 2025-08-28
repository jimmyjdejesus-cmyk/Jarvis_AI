import jarvis.agents.mission_planner as agent_mp
from jarvis.orchestration.mission_planner import MissionPlanner
from jarvis.world_model.knowledge_graph import KnowledgeGraph


class DummyQueue:
    def __init__(self):
        self.tasks = []

    def enqueue(self, task):
        self.tasks.append(task)


def test_team_assignment_and_subdag(monkeypatch):
    responses = iter([
        '{"tasks": ["exploit system", "defend network"]}',
        '{"tasks": ["identify vulnerability", "develop exploit"]}',
        '{"tasks": ["analyze defenses", "deploy patches"]}',
    ])
    monkeypatch.setattr(
        agent_mp.model_client,
        "generate_response",
        lambda model, prompt: next(responses),
    )

    kg = KnowledgeGraph()
    kg.add_fact("red", "capable_of", "exploit")
    kg.add_fact("blue", "capable_of", "defend")

    queue = DummyQueue()
    planner = MissionPlanner(
        missions_dir="config/missions",
        queue=queue,
        knowledge_graph=kg,
    )
    dag = planner.plan(goal="security audit", context={})

    assert len(dag.nodes) > 2  # sub-DAG nodes added
    assert queue.tasks[0]["team"] == "red"
    assert queue.tasks[1]["team"] == "blue"
    assert any(
        t["id"].startswith("task_1_") for t in queue.tasks
    )
