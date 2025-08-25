"""Tests for the v2 workflow visualiser and export endpoint."""

import os
import sys

from fastapi.testclient import TestClient

# Ensure the repository root is on the Python path for ``v2`` imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from v2.agent.adapters.langgraph_ui import WorkflowVisualizer
from v2.run import app, visualizer


def test_visualizer_export_formats() -> None:
    """The visualiser should export to JSON and DOT."""

    viz = WorkflowVisualizer()
    viz.add_event(
        {
            "id": "team1",
            "type": "Team",
            "label": "Team A",
            "color": "red",
            "produces": ["call1"],
            "scope": "team",
            "status": "active",
            "score": 0.9,
        }
    )
    viz.add_event(
        {
            "id": "call1",
            "type": "ToolCall",
            "label": "Tool",
            "status": "pruned",
        }
    )

    data = viz.export("json")
    assert {n["id"] for n in data["nodes"]} == {"team1", "call1"}
    assert any(e["type"] == "produces" for e in data["edges"])

    dot = viz.export("dot")
    assert "team1" in dot and "call1" in dot


def test_export_route() -> None:
    """The FastAPI endpoint should return the requested format."""

    client = TestClient(app)

    # Reset global visualiser state and populate with a simple node
    visualizer.nodes.clear()
    visualizer.edges.clear()
    visualizer.add_event({"id": "a", "type": "Team"})

    resp = client.get("/graph/export?format=json")
    assert resp.status_code == 200
    assert resp.json()["nodes"][0]["id"] == "a"

    resp = client.get("/graph/export?format=dot")
    assert resp.status_code == 200
    assert "a" in resp.text

