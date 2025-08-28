import unittest
from unittest.mock import MagicMock

from jarvis.ecosystem.meta_intelligence import ExecutiveAgent
from jarvis.orchestration.mission import MissionDAG, MissionNode


class TestExecutiveAgentPlan(unittest.TestCase):
    def test_plan_spawns_sub_orchestrators(self):
        dag = MissionDAG(
            mission_id="m1",
            nodes={
                "s1": MissionNode(step_id="s1", capability="cap", team_scope="team"),
            },
        )
        planner = MagicMock()
        planner.plan.return_value = dag

        agent = ExecutiveAgent("exec", mission_planner=planner)
        agent.orchestrator.create_child_orchestrator = MagicMock()
        agent.plan("goal", {})
        agent.orchestrator.create_child_orchestrator.assert_called_with(
            "team", {"mission_name": "team"}
        )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
