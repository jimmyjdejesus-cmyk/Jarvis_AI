import threading

import fakeredis
import redis

from jarvis.agents.curiosity_router import CuriosityRouter, PersistentQueue


def test_curiosity_router_enqueues_and_dequeues() -> None:
    """Router pushes sanitized directive to Redis-backed queue."""

    fake = fakeredis.FakeRedis()
    queue = PersistentQueue(client=fake)
    router = CuriosityRouter(queue=queue)
    router.route("Explore vacuum energy?")

    task = queue.dequeue()
    assert task == {
        "type": "directive",
        "request": "Investigate: Explore vacuum energy",
    }


def test_curiosity_router_disabled() -> None:
    fake = fakeredis.FakeRedis()
    queue = PersistentQueue(client=fake)
    router = CuriosityRouter(queue=queue, enabled=False)
    router.route("Ignore me")
    assert queue.dequeue() is None


class FailingRedis:
    def rpush(self, *args, **kwargs):  # noqa: D401 - simple failure stub
        raise redis.ConnectionError("boom")

    def lpop(self, *args, **kwargs):
        raise redis.ConnectionError("boom")


def test_queue_fallback_on_redis_failure() -> None:
    queue = PersistentQueue(client=FailingRedis())
    router = CuriosityRouter(queue=queue)
    router.route("Test failure?")
    task = queue.dequeue()
    assert task == {
        "type": "directive",
        "request": "Investigate: Test failure",
    }


def test_local_backlog_drained_first() -> None:
    """Items queued during outages are processed before Redis items."""

    # enqueue while redis is down so items go to local fallback
    queue = PersistentQueue(client=FailingRedis())
    router = CuriosityRouter(queue=queue)
    router.route("Offline A?")
    router.route("Offline B?")

    # restore redis and enqueue a new item that should be processed last
    queue.client = fakeredis.FakeRedis()
    router.route("Online C?")

    assert queue.dequeue()["request"].endswith("Offline A")
    assert queue.dequeue()["request"].endswith("Offline B")
    assert queue.dequeue()["request"].endswith("Online C")


def test_persistent_queue_threadsafe() -> None:
    queue = PersistentQueue(client=None)  # use in-memory queue

    def worker(i: int) -> None:
        queue.enqueue({"id": i})

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    results = sorted(queue.dequeue()["id"] for _ in range(10))
    assert results == list(range(10))
