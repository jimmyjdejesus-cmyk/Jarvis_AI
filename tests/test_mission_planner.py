import unittest
from unittest.mock import MagicMock, patch
import json
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from jarvis.agents.mission_planner import MissionPlanner

class TestMissionPlanner(unittest.TestCase):

    @patch('jarvis.models.client.model_client')
    def test_plan_generates_multi_step_plan(self, mock_model_client):
        # Mock the model client's response
        mock_model_client.generate_response.return_value = '{"tasks": ["task 1", "task 2", "task 3"]}'

        # Instantiate the planner, the client is now mocked globally
        planner = MissionPlanner(client=mock_model_client)

        # Call the plan method
        dag = planner.plan("test goal", {})

        # Assert that the DAG has multiple nodes
        self.assertGreater(len(dag.nodes), 1)

        # Assert that the tasks from the LLM are in the nodes
        self.assertIn("task_1", dag.nodes)
        self.assertEqual(dag.nodes["task_1"].details, "task 1")
        self.assertIn("task_2", dag.nodes)
        self.assertEqual(dag.nodes["task_2"].details, "task 2")
        self.assertIn("task_3", dag.nodes)
        self.assertEqual(dag.nodes["task_3"].details, "task 3")

if __name__ == '__main__':
    unittest.main()
