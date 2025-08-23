import os
import sys
import pytest

pytest.importorskip("graphviz")

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agent.ui.dag_panel import WorkflowVisualizer, StepEvent


def test_workflow_visualizer_logs_and_graph():
    viz = WorkflowVisualizer()
    e1 = StepEvent(
        run_id="r1",
        step_id="a",
        parent_id=None,
        event_type="ToolCall",
        payload={},
        tool="search",
        agent="researcher",
        reasoning="initial"
    )
    e2 = StepEvent(
        run_id="r1",
        step_id="b",
        parent_id="a",
        event_type="ToolCall",
        payload={},
        tool="calc",
        agent="analyst",
        status="pruned",
        reasoning="not needed"
    )
    e3 = StepEvent(
        run_id="r1",
        step_id="c",
        parent_id=None,
        event_type="Merge",
        payload={},
        agent="manager",
        status="merged",
        merged_from=["a", "b"],
        reasoning="combine"
    )
    viz.add_event(e1)
    viz.add_event(e2)
    viz.add_event(e3)

    dot = viz._build_graph()
    src = dot.source
    assert "color=red" in src
    assert "color=blue" in src
    assert "search" in src and "researcher" in src

    log = viz.render_event_log(show_reasoning=True)
    assert any("reason=" in line for line in log)
