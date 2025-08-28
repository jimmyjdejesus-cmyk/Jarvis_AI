import asyncio
import unittest
from unittest.mock import MagicMock, patch

from jarvis.ecosystem.meta_intelligence import ExecutiveAgent
from jarvis.workflows.engine import WorkflowStatus


class TestExecutiveAgent(unittest.TestCase):
    """Tests for :class:`ExecutiveAgent` mission execution."""

    @patch("jarvis.ecosystem.meta_intelligence.workflow_engine.execute_workflow")
    @patch("jarvis.ecosystem.meta_intelligence.MissionDAG.from_dict")
    @patch.object(ExecutiveAgent, "manage_directive")
    def test_execute_mission_success(
        self, mock_manage_directive, mock_from_dict, mock_execute
    ) -> None:
        """Mission executes successfully when planning succeeds."""
        mock_manage_directive.return_value = {"success": True, "tasks": [], "graph": {}}
        mock_from_dict.return_value = MagicMock()

        completed = MagicMock()
        completed.status = WorkflowStatus.COMPLETED
        completed.workflow_id = "wf1"
        completed.context.results = {"step": MagicMock(output="ok")}

        async def _run(_workflow):
            return completed

        mock_execute.side_effect = _run

        agent = ExecutiveAgent("agent")
        result = asyncio.run(agent.execute_mission("do things", {}))
        self.assertTrue(result["success"])
        self.assertEqual(result["results"]["status"], "completed")
        mock_manage_directive.assert_called_once()
        mock_execute.assert_called_once()

    @patch.object(ExecutiveAgent, "manage_directive")
    def test_execute_mission_planning_failure(self, mock_manage_directive) -> None:
        """Mission returns error information when planning fails."""
        mock_manage_directive.return_value = {
            "success": False,
            "critique": {"message": "bad"},
        }
        agent = ExecutiveAgent("agent")
        result = asyncio.run(agent.execute_mission("do", {}))
        self.assertFalse(result["success"])
        self.assertIn("Mission planning failed", result["error"])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
