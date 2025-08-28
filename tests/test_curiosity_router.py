from jarvis.agents.curiosity_router import CuriosityRouter


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
