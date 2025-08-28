import asyncio
import importlib.util
import pathlib
import sys
import types
import pytest
from unittest.mock import AsyncMock


def load_orchestrator():
    root = pathlib.Path(__file__).resolve().parents[1] / "jarvis"
    jarvis_stub = types.ModuleType("jarvis")
    jarvis_stub.__path__ = [str(root)]
    sys.modules.setdefault("jarvis", jarvis_stub)
    orch_stub = types.ModuleType("jarvis.orchestration")
    orch_stub.__path__ = [str(root / "orchestration")]
    sys.modules.setdefault("jarvis.orchestration", orch_stub)
    spec = importlib.util.spec_from_file_location(
        "jarvis.orchestration.orchestrator",
        root / "orchestration" / "orchestrator.py",
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


orchestrator_module = load_orchestrator()
MultiAgentOrchestrator = orchestrator_module.MultiAgentOrchestrator
StepContext = orchestrator_module.StepContext
performance_spec = importlib.util.spec_from_file_location(
    "jarvis.monitoring.performance",
    pathlib.Path(__file__).resolve().parents[1]
    / "jarvis/monitoring/performance.py",
)
performance_module = importlib.util.module_from_spec(performance_spec)
sys.modules[performance_spec.name] = performance_module
performance_spec.loader.exec_module(performance_module)
PerformanceTracker = performance_module.PerformanceTracker


class DummyMcpClient:
    async def generate_response(self, server, model, prompt):
        if "Analyze" in prompt:
            return (
                '{"specialists_needed": ["testspecialist"], '
                '"complexity": "low"}'
            )
        if "constitutional critic" in prompt:
            return '{"veto": false, "violations": []}'
        return "response"


class DummySpecialist:
    def __init__(self, name="test_specialist"):
        self.name = name

    async def process_task(self, task, **kwargs):
        return {"response": f"{self.name} processed {task}"}


@pytest.mark.asyncio
async def test_orchestrator_with_critic():
    mcp_client = DummyMcpClient()
    orchestrator = MultiAgentOrchestrator(mcp_client, specialists={})
    orchestrator.specialists = {"testspecialist": DummySpecialist()}

    result = await orchestrator.coordinate_specialists("test request")
    assert result["synthesized_response"] == "response"


@pytest.mark.asyncio
async def test_orchestrator_with_critic_veto():
    mcp_client = DummyMcpClient()
    orchestrator = MultiAgentOrchestrator(mcp_client, specialists={})
    orchestrator.specialists = {"testspecialist": DummySpecialist()}

    async def mock_review(plan):
        return {"veto": True, "violations": ["test violation"]}

    orchestrator.critic.review = mock_review

    result = await orchestrator.coordinate_specialists("test request")
    assert result["error"] is True
    assert "test violation" in result["synthesized_response"]


@pytest.mark.asyncio
async def test_dispatch_with_retry():
    mcp_client = DummyMcpClient()
    orchestrator = MultiAgentOrchestrator(mcp_client, specialists={})

    specialist = DummySpecialist()
    specialist.process_task = AsyncMock(
        side_effect=[Exception("fail"), {"response": "success"}]
    )
    orchestrator.specialists = {"testspecialist": specialist}

    result = await orchestrator.dispatch_specialist("test_specialist", "test")
    assert result == {"response": "success"}
    assert specialist.process_task.call_count == 2


@pytest.mark.asyncio
async def test_dispatch_with_timeout():
    mcp_client = DummyMcpClient()
    orchestrator = MultiAgentOrchestrator(mcp_client, specialists={})

    async def slow_task(*args, **kwargs):
        await asyncio.sleep(0.2)
        return {"response": "success"}

    specialist = DummySpecialist()
    specialist.process_task = slow_task
    orchestrator.specialists = {"test_specialist": specialist}

    with pytest.raises(asyncio.TimeoutError):
        await orchestrator.dispatch_specialist("test_specialist", "test")


@pytest.mark.asyncio
async def test_run_step_retry_backoff(monkeypatch):
    mcp_client = DummyMcpClient()
    tracker = PerformanceTracker()
    orchestrator = MultiAgentOrchestrator(
        mcp_client, performance_tracker=tracker, specialists={}
    )

    orchestrator.coordinate_specialists = AsyncMock(
        side_effect=[
            Exception("fail"),
            {"response": "ok", "specialists_used": []},
        ]
    )

    sleep_calls = []

    async def fake_sleep(duration):
        sleep_calls.append(duration)

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    step_ctx = StepContext(
        request="test",
        retry_policy={"retries": 1, "backoff_base": 0.1},
    )

    result = await orchestrator.run_step(step_ctx)

    assert result.data["response"] == "ok"
    assert sleep_calls == [0.1]
    assert tracker.metrics["failed_steps"] == 1


@pytest.mark.asyncio
async def test_run_step_timeout_records_failure():
    mcp_client = DummyMcpClient()
    tracker = PerformanceTracker()
    orchestrator = MultiAgentOrchestrator(
        mcp_client, performance_tracker=tracker, specialists={}
    )

    async def slow_cs(*args, **kwargs):
        await asyncio.sleep(0.05)
        return {"response": "late"}

    orchestrator.coordinate_specialists = slow_cs

    step_ctx = StepContext(request="test", timeout=0.01)

    with pytest.raises(asyncio.TimeoutError):
        await orchestrator.run_step(step_ctx)

    assert tracker.metrics["failed_steps"] == 1
