import asyncio
from unittest.mock import MagicMock, patch
import pytest

try:
    from jarvis.ecosystem.meta_intelligence import ExecutiveAgent
    from jarvis.workflows.engine import WorkflowStatus
except Exception:  # pragma: no cover - module may be unavailable
    ExecutiveAgent = None
    WorkflowStatus = MagicMock()


@pytest.mark.skipif(ExecutiveAgent is None, reason="ExecutiveAgent not available")
def test_execute_mission_updates_graph(mock_neo4j_graph):
    """`execute_mission` should persist mission nodes and edges."""
    agent = ExecutiveAgent("agent")

    fake_mission = MagicMock()

    async def _run_workflow(_workflow):
        completed = MagicMock()
        completed.status = WorkflowStatus.COMPLETED
        completed.workflow_id = "wf1"
        completed.context.results = []
        return completed

    def fake_update_world_model(self, mission, results):
        mock_neo4j_graph.add_node("m1", "mission")
        mock_neo4j_graph.add_edge("m1", "s1", "HAS_STEP")

    with patch.object(ExecutiveAgent, "manage_directive", return_value={"success": True, "tasks": [], "graph": {}}), \
         patch("jarvis.ecosystem.meta_intelligence.MissionDAG.from_dict", return_value=fake_mission), \
         patch("jarvis.ecosystem.meta_intelligence.workflow_engine.execute_workflow", side_effect=_run_workflow), \
         patch.object(ExecutiveAgent, "_update_world_model", fake_update_world_model):
        asyncio.run(agent.execute_mission("do", {}))

    mock_neo4j_graph.add_node.assert_called_with("m1", "mission")
    mock_neo4j_graph.add_edge.assert_called_with("m1", "s1", "HAS_STEP")
