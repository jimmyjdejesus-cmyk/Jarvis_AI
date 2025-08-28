import unittest
from unittest.mock import patch

from jarvis.orchestration.sub_orchestrator import SubOrchestrator
from jarvis.orchestration.orchestrator import MultiAgentOrchestrator
from jarvis.orchestration.mission import MissionDAG, MissionNode
import asyncio


class TestSubOrchestrator(unittest.TestCase):
    def test_allowed_specialists_filter(self):
        fake_specialists = {"a": object(), "b": object()}

        def fake_init(self, *args, **kwargs):
            self.specialists = fake_specialists

        with patch.object(MultiAgentOrchestrator, "__init__", fake_init):
            orchestrator = SubOrchestrator(None, allowed_specialists=["a"])

        self.assertEqual(list(orchestrator.specialists.keys()), ["a"])

    def test_run_mission_dag_rejects_unallowed_specialist(self):
        fake_specialists = {"a": object()}

        def fake_init(self, *args, **kwargs):
            self.specialists = fake_specialists
            self.child_orchestrators = {}

        dag = MissionDAG(
            mission_id="m1",
            nodes={
                "s1": MissionNode(step_id="s1", capability="cap", team_scope="b"),
            },
        )

        with patch.object(MultiAgentOrchestrator, "__init__", fake_init):
            orchestrator = SubOrchestrator(None, allowed_specialists=["a"])

        with self.assertRaises(ValueError):
            asyncio.run(orchestrator.run_mission_dag(dag))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
