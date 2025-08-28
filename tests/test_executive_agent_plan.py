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
            "team", {"mission_name": "team", "allowed_specialists": ["team"]}
        )

    def test_child_orchestrator_restricts_specialists(self):
        dag = MissionDAG(
            mission_id="m1",
            nodes={
                "s1": MissionNode(step_id="s1", capability="cap", team_scope="team"),
            },
        )
        planner = MagicMock()
        planner.plan.return_value = dag

        agent = ExecutiveAgent("exec", mission_planner=planner)
        fake_specialists = {"team": object(), "other": object()}

        def fake_create_child(name, spec):
            from jarvis.orchestration.sub_orchestrator import SubOrchestrator

            child = SubOrchestrator(
                None,
                allowed_specialists=spec.get("allowed_specialists"),
                custom_specialists=fake_specialists,
            )
            agent.orchestrator.child_orchestrators[name] = child
            return child

        agent.orchestrator.create_child_orchestrator = fake_create_child
        agent.plan("goal", {})
        child = agent.orchestrator.child_orchestrators["team"]
        self.assertEqual(set(child.specialists.keys()), {"team"})


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
