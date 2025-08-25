import sys
import importlib.util
import types
from pathlib import Path
from typing import Dict, Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

# Stub tracing module required by WorkflowEngine
trace_mod = types.ModuleType("jarvis.observability.tracing")
def _trace(name, metadata=None):  # pragma: no cover - simple stub
    class Ctx:
        def __enter__(self):
            return None
        def __exit__(self, exc_type, exc, tb):
            return False
    return Ctx()
trace_mod.trace = _trace
obs_pkg = types.ModuleType("jarvis.observability")
obs_pkg.tracing = trace_mod
sys.modules["jarvis"] = types.ModuleType("jarvis")
sys.modules["jarvis.observability"] = obs_pkg
sys.modules["jarvis.observability.tracing"] = trace_mod

spec = importlib.util.spec_from_file_location(
    "jarvis.orchestration.mission", ROOT / "jarvis" / "orchestration" / "mission.py"
)
mission_module = importlib.util.module_from_spec(spec)
sys.modules["jarvis.orchestration.mission"] = mission_module
spec.loader.exec_module(mission_module)

from agent.features.workflow_system import Task, TaskState, WorkflowEngine
from jarvis.orchestration.mission import (
    Mission,
    MissionDAG,
    MissionNode,
    save_mission,
    load_mission,
    update_node_state,
)


def test_interrupt_mid_mission_restart_resumes(tmp_path, monkeypatch):
    monkeypatch.setattr(mission_module, "MISSION_DIR", str(tmp_path))

    nodes = {
        "t1": MissionNode(step_id="t1", capability="a", team_scope="core"),
        "t2": MissionNode(step_id="t2", capability="b", team_scope="core", deps=["t1"]),
    }
    dag = MissionDAG(mission_id="m1", nodes=nodes, edges=[("t1", "t2")])
    mission = Mission(id="m1", title="test", goal="g", inputs={}, risk_level="low", dag=dag)
    save_mission(mission)

    def handler(event):
        if event.step_id == "t2" and event.event_type == "start":
            raise KeyboardInterrupt

    engine = WorkflowEngine(
        storage_dir=str(tmp_path), event_handler=handler, state_handler=update_node_state
    )
    tasks = [
        Task(id="t1", fn=lambda ctx: ctx.setdefault("seq", []).append("t1")),
        Task(id="t2", fn=lambda ctx: ctx.setdefault("seq", []).append("t2"), depends_on=["t1"]),
    ]
    wf = engine.create_workflow(tasks, run_id="m1")
    context: Dict[str, Any] = {}
    try:
        engine.run(wf, context)
    except KeyboardInterrupt:
        pass

    m = load_mission("m1")
    assert m.dag.nodes["t1"].state.status == "succeeded"
    assert m.dag.nodes["t2"].state.status == "pending"

    wf2 = engine.load_workflow("m1")
    wf2.tasks["t1"].fn = lambda ctx: ctx.setdefault("seq", []).append("t1")
    wf2.tasks["t2"].fn = lambda ctx: ctx.setdefault("seq", []).append("t2")
    wf2.tasks["t1"].state = TaskState.COMPLETED
    wf2.tasks["t2"].state = TaskState.PENDING
    engine2 = WorkflowEngine(
        storage_dir=str(tmp_path), event_handler=lambda e: None, state_handler=update_node_state
    )
    engine2.run(wf2, context)

    m2 = load_mission("m1")
    assert m2.dag.nodes["t2"].state.status == "succeeded"
