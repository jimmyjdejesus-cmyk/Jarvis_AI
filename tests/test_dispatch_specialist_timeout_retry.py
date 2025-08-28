import asyncio
import logging

import pytest

from jarvis.orchestration.orchestrator import MultiAgentOrchestrator


class DummySpecialist:
    """Specialist stub used for testing dispatch logic."""

    def __init__(self, behavior):
        self.behavior = behavior
        self.calls = 0

    async def process_task(self, task, **kwargs):
        self.calls += 1
        return await self.behavior(task, **kwargs)


def test_dispatch_specialist_timeout():
    async def slow(task, **kwargs):
        await asyncio.sleep(0.2)
        return {"type": "success"}

    specialist = DummySpecialist(slow)
    orchestrator = MultiAgentOrchestrator(None, specialists={"dummy": specialist})

    with pytest.raises(asyncio.TimeoutError):
        asyncio.run(
            orchestrator.dispatch_specialist(
                "dummy", "task", timeout=0.05, retries=2
            )
        )
    assert specialist.calls == 2


def test_dispatch_specialist_retries(caplog):
    async def failing(task, **kwargs):
        raise ValueError("fail")

    specialist = DummySpecialist(failing)
    orchestrator = MultiAgentOrchestrator(None, specialists={"dummy": specialist})

    with caplog.at_level(logging.WARNING):
        with pytest.raises(ValueError):
            asyncio.run(
                orchestrator.dispatch_specialist(
                    "dummy", "task", retries=2, timeout=0.05
                )
            )

    assert specialist.calls == 2
    assert "Attempt 1/2 for dummy failed" in caplog.text
    assert "Attempt 2/2 for dummy failed" in caplog.text


def test_dispatch_specialist_retry_success(caplog):
    async def flaky(task, **kwargs):
        if flaky.fail:
            flaky.fail = False
            raise ValueError("fail once")
        return {"type": "ok"}

    flaky.fail = True
    specialist = DummySpecialist(flaky)
    orchestrator = MultiAgentOrchestrator(None, specialists={"dummy": specialist})

    with caplog.at_level(logging.WARNING):
        result = asyncio.run(
            orchestrator.dispatch_specialist("dummy", "task", retries=2, timeout=0.05)
        )

    assert result == {"type": "ok"}
    assert specialist.calls == 2
    assert "Attempt 1/2 for dummy failed" in caplog.text
