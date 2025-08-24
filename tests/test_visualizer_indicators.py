import importlib
import sys
from pathlib import Path


def test_visualizer_indicators():
    sys.modules.pop("ui", None)
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    viz_mod = importlib.import_module("ui.visualizer")
    WorkflowVisualizer = viz_mod.WorkflowVisualizer

    events = [
        {"run_id": "r1", "step_id": "A", "status": "active"},
        {"run_id": "r1", "step_id": "B", "status": "pruned", "parent_id": "A"},
        {
            "run_id": "r1",
            "step_id": "C",
            "status": "active",
            "merged_from": ["B"],
            "parent_id": "A",
        },
    ]
    viz = WorkflowVisualizer(events)
    graph = viz._build_graph()
    dot = "\n".join(graph.body)
    assert "A" in dot and "color=green" in dot
    assert "B" in dot and "color=red" in dot
    assert "B -> C" in dot and "style=dashed" in dot
