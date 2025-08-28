import unittest
import asyncio
from unittest.mock import patch, MagicMock

from jarvis.orchestration.mission import MissionDAG, MissionNode
from jarvis.workflows.engine import (
    from_mission_dag,
    WorkflowEngine,
    TaskStatus,
    WorkflowStatus,
)


class TestWorkflowEngine(unittest.TestCase):

    def test_from_mission_dag_conversion(self):
        # Create a sample MissionDAG
        nodes = {
            "task_1": MissionNode(
                step_id="task_1",
                capability="test_capability_1",
                team_scope="test_scope_1",
                details="details for task 1",
            ),
            "task_2": MissionNode(
                step_id="task_2",
                capability="test_capability_2",
                team_scope="test_scope_2",
                deps=["task_1"],
            ),
        }
        dag = MissionDAG(mission_id="test_mission", nodes=nodes)

        # Convert to workflow
        workflow = from_mission_dag(dag)

        self.assertEqual(workflow.name, "test_mission")
        self.assertEqual(len(workflow.tasks), 2)
        self.assertEqual(workflow.tasks[0].name, "task_1")
        self.assertEqual(workflow.tasks[1].dependencies, ["task_1"])

    @patch("jarvis.workflows.engine.SpecialistTask.execute")
    def test_workflow_execution(self, mock_execute):
        # Mock the execute method to return a successful result
        async def mock_execute_side_effect(context):
            return MagicMock(status=TaskStatus.COMPLETED)
        mock_execute.side_effect = mock_execute_side_effect

        # Create a sample MissionDAG
        nodes = {
            "task_1": MissionNode(
                step_id="task_1",
                capability="test",
                team_scope="test",
                details="details 1",
            ),
            "task_2": MissionNode(
                step_id="task_2",
                capability="test",
                team_scope="test",
                deps=["task_1"],
            ),
        }
        dag = MissionDAG(mission_id="test_mission_2", nodes=nodes)

        # Convert and execute
        workflow = from_mission_dag(dag)
        engine = WorkflowEngine()

        # Run the async execute_workflow method
        completed_workflow = asyncio.run(
            engine.execute_workflow(workflow)
        )

        # Assertions
        self.assertEqual(completed_workflow.status, WorkflowStatus.COMPLETED)
        self.assertEqual(len(completed_workflow.context.results), 2)
        self.assertEqual(mock_execute.call_count, 2)


if __name__ == "__main__":
    unittest.main()
