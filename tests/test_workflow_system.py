import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import json
from pathlib import Path

from agent.features.workflow_system import Task, TaskState, WorkflowEngine


def test_engine_executes_and_persists(tmp_path):
    events = []
    engine = WorkflowEngine(storage_dir=str(tmp_path), event_handler=events.append)

    def step_a(ctx):
        ctx["a"] = 1
        return "A"

    def step_b(ctx):
        assert ctx["a"] == 1
        return "B"

    t1 = Task(id="a", fn=step_a)
    t2 = Task(id="b", fn=step_b, depends_on=["a"])
    wf = engine.create_workflow([t1, t2])

    engine.run(wf, context={})

    assert wf.tasks["a"].state is TaskState.COMPLETED
    assert wf.tasks["b"].state is TaskState.COMPLETED

    # events persisted
    event_types = [e.event_type for e in events]
    assert event_types.count("start") == 2
    assert event_types.count("complete") == 2

    def_file = Path(tmp_path) / f"{wf.id}_definition.json"
    events_file = Path(tmp_path) / f"{wf.id}_events.json"
    assert def_file.exists() and events_file.exists()

    # replay
    loaded = engine.load_workflow(wf.id)
    assert loaded.id == wf.id

    replayed = engine.replay_events(wf.id)
    assert len(replayed) == len(events)

