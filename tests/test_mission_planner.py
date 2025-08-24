import yaml
import fakeredis

from jarvis.orchestration.mission_planner import MissionPlanner
from jarvis.orchestration.task_queue import RedisTaskQueue
from jarvis.orchestration.agents import MetaAgent


def test_mission_planner_enqueue(tmp_path):
    missions_dir = tmp_path / "missions"
    missions_dir.mkdir()
    mission_data = {
        "goal": "Test mission",
        "tasks": [{"id": "t1", "description": "First"}],
    }
    with open(missions_dir / "demo.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(mission_data, f)

    fake_r = fakeredis.FakeRedis(decode_responses=True)
    queue = RedisTaskQueue(name="demo", redis_client=fake_r)
    planner = MissionPlanner(str(missions_dir), queue=queue)

    tasks = planner.plan("demo")

    assert len(tasks) == 1
    assert queue.length() == 1
    task = queue.dequeue()
    assert task == mission_data["tasks"][0]


def test_meta_agent_plan_mission(tmp_path):
    base_dir = tmp_path
    missions_dir = base_dir / "config" / "missions"
    missions_dir.mkdir(parents=True)
    data = {"goal": "Meta goal", "tasks": [{"id": "x", "description": "Do X"}]}
    with open(missions_dir / "meta.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)

    fake_r = fakeredis.FakeRedis(decode_responses=True)
    queue = RedisTaskQueue(name="meta", redis_client=fake_r)
    planner = MissionPlanner(str(missions_dir), queue=queue)

    meta = MetaAgent(directory=str(base_dir))
    meta.mission_planner = planner

    tasks = meta.plan_mission("meta")
    assert len(tasks) == 1
    assert meta.next_task()["id"] == "x"
