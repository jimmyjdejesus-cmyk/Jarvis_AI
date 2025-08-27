import unittest
import asyncio
from unittest.mock import patch, MagicMock

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from jarvis.ecosystem.meta_intelligence import ExecutiveAgent
from jarvis.orchestration.mission import MissionDAG, MissionNode
from jarvis.workflows.engine import WorkflowStatus

class TestExecutiveAgent(unittest.TestCase):

    @patch('jarvis.ecosystem.meta_intelligence.WorkflowEngine')
    @patch('jarvis.ecosystem.meta_intelligence.MissionPlanner')
    def test_execute_mission(self, mock_mission_planner, mock_workflow_engine):
        # Mock MissionPlanner
        mock_planner_instance = mock_mission_planner.return_value
        nodes = {
            "task_1": MissionNode(step_id="task_1", capability="test", team_scope="test", details="details 1"),
        }
        dag = MissionDAG(mission_id="test_mission", nodes=nodes)
        mock_planner_instance.plan.return_value = dag

        # Mock WorkflowEngine
        mock_engine_instance = mock_workflow_engine.return_value

        # Create a mock for the completed workflow object
        completed_workflow_mock = MagicMock()
        completed_workflow_mock.status = WorkflowStatus.COMPLETED
        completed_workflow_mock.workflow_id = "test_workflow"

        # Set up the context and results as they would be in the real object
        completed_workflow_mock.context.results = {
            "task_1": MagicMock(output="task 1 output")
        }

        async def mock_execute_workflow(*args, **kwargs):
            return completed_workflow_mock

        mock_engine_instance.execute_workflow.side_effect = mock_execute_workflow

        # Instantiate ExecutiveAgent
        agent = ExecutiveAgent(agent_id="test_agent")

        # Run the async execute_mission method
        result = asyncio.run(agent.execute_mission("test mission", {}))

        # Assertions
        self.assertTrue(result["success"])
        self.assertEqual(result["results"]["status"], "completed")
        mock_planner_instance.plan.assert_called_once_with("test mission", {})
        mock_workflow_engine.assert_called_once()
        mock_engine_instance.execute_workflow.assert_called_once()


if __name__ == '__main__':
    unittest.main()
