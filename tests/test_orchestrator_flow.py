import asyncio
import importlib.util
import json
import pathlib
import sys
import types
import pytest
from unittest.mock import AsyncMock


def load_orchestrator():
    """Load the `MultiAgentOrchestrator` module with stubbed packages."""
    root = pathlib.Path(__file__).resolve().parents[1] / "jarvis"
    jarvis_stub = types.ModuleType("jarvis")
    jarvis_stub.__path__ = [str(root)]
    sys.modules.setdefault("jarvis", jarvis_stub)
    orch_stub = types.ModuleType("jarvis.orchestration")
    orch_stub.__path__ = [str(root / "orchestration")]
    sys.modules.setdefault("jarvis.orchestration", orch_stub)
    orchestrator_path = root / "orchestration" / "orchestrator.py"
    spec = importlib.util.spec_from_file_location(
        "jarvis.orchestration.orchestrator", orchestrator_path
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


orchestrator_module = load_orchestrator()
MultiAgentOrchestrator = orchestrator_module.MultiAgentOrchestrator
StepContext = orchestrator_module.StepContext
performance_root = pathlib.Path(__file__).resolve().parents[1]
performance_path = performance_root / "jarvis/monitoring/performance.py"
performance_spec = importlib.util.spec_from_file_location(
    "jarvis.monitoring.performance", performance_path
)
performance_module = importlib.util.module_from_spec(performance_spec)
sys.modules[performance_spec.name] = performance_module
performance_spec.loader.exec_module(performance_module)
PerformanceTracker = performance_module.PerformanceTracker


class DummyMcpClient:
    async def generate_response(self, server, model, prompt):
        if "Analyze" in prompt:
            data = {
                "specialists_needed": ["test_specialist"],
                "complexity": "low",
            }
            return json.dumps(data)
        if "constitutional critic" in prompt:
            return '{"veto": false, "violations": []}'
        return "response"


class DummySpecialist:
    def __init__(self, name="test_specialist"):
        self.name = name
        self.preferred_models: list[str] = []

    async def process_task(self, task, **kwargs):
        return {"response": "response"}


class IncompleteSpecialist(DummySpecialist):
    async def process_task(self, task, **kwargs):
        return {"confidence": 0.5}


@pytest.mark.asyncio
async def test_orchestrator_with_critic():
    mcp_client = DummyMcpClient()
    orchestrator = MultiAgentOrchestrator(mcp_client, specialists={})
    orchestrator.specialists = {"test_specialist": DummySpecialist()}

    result = await orchestrator.coordinate_specialists("test request")
    assert result["synthesized_response"] == "response"


@pytest.mark.asyncio
async def test_orchestrator_with_critic_veto():
    mcp_client = DummyMcpClient()
    orchestrator = MultiAgentOrchestrator(mcp_client, specialists={})
    orchestrator.specialists = {"test_specialist": DummySpecialist()}

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
    orchestrator.specialists = {"test_specialist": specialist}

    with pytest.raises(Exception) as e:
        await orchestrator.dispatch_specialist("test_specialist", "test")
    assert "Task failed after 3 retries" in str(e.value)
    assert specialist.process_task.call_count == 3


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

    with pytest.raises(Exception) as e:
        await orchestrator.dispatch_specialist("test_specialist", "test")

    assert "Task failed after 3 retries" in str(e.value)


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


@pytest.mark.asyncio
async def test_dispatch_unknown_specialist_raises():
    """Dispatching an unregistered specialist should raise ValueError."""
    mcp_client = DummyMcpClient()
    orchestrator = MultiAgentOrchestrator(mcp_client, specialists={})

    with pytest.raises(ValueError):
        await orchestrator.dispatch_specialist("ghost", "test")


@pytest.mark.asyncio
async def test_coordinate_specialists_missing_specialist():
    """Coordinator returns error when analysis requests missing specialist."""

    class MissingSpecClient(DummyMcpClient):
        async def generate_response(self, server, model, prompt):  # noqa: D401
            return json.dumps(
                {"specialists_needed": ["ghost"], "complexity": "low"}
            )

    mcp_client = MissingSpecClient()
    orchestrator = MultiAgentOrchestrator(mcp_client, specialists={})

    result = await orchestrator.coordinate_specialists("test request")
    assert result["error"] is True
    assert "Unknown specialist" in result["synthesized_response"]


@pytest.mark.asyncio
async def test_coordinate_specialists_invalid_json():
    """Invalid JSON analysis should fall back to simple response."""

    class BadJsonClient(DummyMcpClient):
        async def generate_response(self, server, model, prompt):  # noqa: D401
            return "not json"

    mcp_client = BadJsonClient()
    orchestrator = MultiAgentOrchestrator(mcp_client, specialists={})

    result = await orchestrator.coordinate_specialists("simple request")
    assert result["type"] == "simple"
    assert result["specialists_used"] == []


@pytest.mark.asyncio
async def test_coordinate_specialists_invalid_structure():
    """Malformed analysis JSON should fall back to simple response."""

    class BadStructureClient(DummyMcpClient):
        async def generate_response(self, server, model, prompt):  # noqa: D401
            return json.dumps({"specialists_needed": "oops", "complexity": 5})

    mcp_client = BadStructureClient()
    orchestrator = MultiAgentOrchestrator(mcp_client, specialists={})

    result = await orchestrator.coordinate_specialists("structure request")
    assert result["type"] == "simple"
    assert result["specialists_used"] == []


@pytest.mark.asyncio
async def test_dispatch_incomplete_response_returns_error():
    """Specialist returning incomplete data should yield error result."""

    mcp_client = DummyMcpClient()
    specialist = IncompleteSpecialist()
    orchestrator = MultiAgentOrchestrator(
        mcp_client, specialists={"test_specialist": specialist}
    )

    result = await orchestrator.dispatch_specialist("test_specialist", "task")
    assert result["type"] == "error"
    assert result["error"] is True


@pytest.mark.asyncio
async def test_coordinate_specialists_incomplete_response():
    """Coordinator handles incomplete specialist responses gracefully."""

    mcp_client = DummyMcpClient()
    specialist = IncompleteSpecialist()
    orchestrator = MultiAgentOrchestrator(mcp_client, specialists={})
    orchestrator.specialists = {"testing": specialist}

    result = await orchestrator.coordinate_specialists("test request")
    spec_result = result["results"]["testing"]
    assert spec_result["error"] is True
    assert result["synthesized_response"].startswith("Analysis failed")


@pytest.mark.asyncio
async def test_coordinate_specialists_partial_failure():
    """One failing specialist should not block other results."""

    class MultiSpecClient(DummyMcpClient):
        async def generate_response(self, server, model, prompt):  # noqa: D401
            if "Analyze" in prompt:
                return json.dumps(
                    {
                        "specialists_needed": ["good", "bad"],
                        "complexity": "high",
                    }
                )
            return await super().generate_response(server, model, prompt)

    mcp_client = MultiSpecClient()
    orchestrator = MultiAgentOrchestrator(
        mcp_client,
        specialists={"good": DummySpecialist(), "bad": DummySpecialist()},
    )
    orchestrator.dispatch_specialist = AsyncMock(
        side_effect=[
            {"specialist": "good", "response": "ok", "confidence": 1.0},
            orchestrator._create_specialist_error("bad", "fail"),
        ]
    )
    orchestrator.critic.review = AsyncMock(
        return_value={"veto": False, "violations": []}
    )

    result = await orchestrator.coordinate_specialists("test request")
    assert result["results"]["bad"]["error"] is True
    assert result["results"]["good"]["response"] == "ok"
