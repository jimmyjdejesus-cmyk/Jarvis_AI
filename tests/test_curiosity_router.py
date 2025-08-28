import importlib.util
from pathlib import Path

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "curiosity_router", root / "jarvis" / "agents" / "curiosity_router.py"
)
module = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = module
spec.loader.exec_module(module)
CuriosityRouter = module.CuriosityRouter


class DummyQueue:
    def __init__(self) -> None:
        self.tasks = []

    def enqueue(self, task):
        self.tasks.append(task)


def test_curiosity_router_enqueues_question():
    queue = DummyQueue()
    router = CuriosityRouter(queue=queue)
    router.route("Explore vacuum energy?")
    assert queue.tasks == [{"type": "directive", "request": "Explore vacuum energy?"}]


def test_curiosity_router_disabled():
    queue = DummyQueue()
    router = CuriosityRouter(queue=queue, enabled=False)
    router.route("Ignore me")
    assert queue.tasks == []
