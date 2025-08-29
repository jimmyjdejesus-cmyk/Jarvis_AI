import importlib.util
import pathlib
import sys
import types
import asyncio


def load_orchestrator() -> types.ModuleType:
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


class DummyMCP:
    async def generate_response(self, server, model, prompt):
        return "synthesis"


class DummySpecialist:
    async def process_task(self, task):  # pragma: no cover - simple stub
        return {"response": task}


def test_parallel_orchestrator_auction_merge():
    mcp = DummyMCP()
    orch = MultiAgentOrchestrator(mcp)
    orch.specialists = {
        "a": DummySpecialist(),
        "b": DummySpecialist(),
    }

    result = asyncio.run(
        orch.coordinate_specialists("question")
    )
    assert result["synthesized_response"] == "synthesis"
