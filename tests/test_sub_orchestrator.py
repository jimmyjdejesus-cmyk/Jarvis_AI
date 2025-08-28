import unittest
from unittest.mock import patch

from jarvis.orchestration.sub_orchestrator import SubOrchestrator
from jarvis.orchestration.orchestrator import MultiAgentOrchestrator


class TestSubOrchestrator(unittest.TestCase):
    def test_allowed_specialists_filter(self):
        fake_specialists = {"a": object(), "b": object()}

        def fake_init(self, *args, **kwargs):
            self.specialists = fake_specialists

        with patch.object(MultiAgentOrchestrator, "__init__", fake_init):
            orchestrator = SubOrchestrator(None, allowed_specialists=["a"])

        self.assertEqual(list(orchestrator.specialists.keys()), ["a"])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
