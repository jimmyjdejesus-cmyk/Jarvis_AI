from unittest.mock import MagicMock
import sys
import types

# Stub memory_service used by orchestrator to avoid qdrant dependency
memory_service = types.ModuleType("memory_service")


class _Dummy:
    def __init__(self, **kwargs):
        pass


def _avoid_negative(_):
    return {"avoid": False, "results": []}


def _record_path(_):
    return None


memory_service.Metrics = _Dummy
memory_service.NegativeCheck = _Dummy
memory_service.Outcome = _Dummy
memory_service.PathRecord = _Dummy
memory_service.PathSignature = _Dummy
memory_service.avoid_negative = _avoid_negative
memory_service.record_path = _record_path
memory_service.vector_store = object()
sys.modules["memory_service"] = memory_service

from jarvis.agents.curiosity_router import CuriosityRouter  # noqa: E402


def test_curiosity_router_converts_question():
    queue = MagicMock()
    router = CuriosityRouter(queue=queue)
    router.route("What is the capital of France?")
    queue.enqueue.assert_called_once()
    task = queue.enqueue.call_args[0][0]
    assert task["request"] == "Investigate: What is the capital of France"


def test_curiosity_router_sanitizes_question():
    queue = MagicMock()
    router = CuriosityRouter(queue=queue)
    router.route("What is\n;the risk?")
    task = queue.enqueue.call_args[0][0]
    assert task["request"] == "Investigate: What is the risk"
