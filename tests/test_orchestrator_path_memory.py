from __future__ import annotations

import sys
import asyncio

sys.path.append('.')

import pytest

from memory_service import _paths, PathRecord, PathSignature, Metrics, Outcome, record_path
from jarvis.orchestration.orchestrator import MultiAgentOrchestrator


class DummyMCP:
    async def generate_response(self, server: str, model: str, prompt: str) -> str:  # pragma: no cover - simple stub
        return "synthesized"


class DummySpecialist:
    def __init__(self, name: str) -> None:
        self.name = name
        self.task_history = []

    async def process_task(self, task, context=None, user_context=None):  # pragma: no cover - simple stub
        self.task_history.append(task)
        return {
            "specialist": self.name,
            "response": f"{self.name} processed",
            "confidence": 0.9,
            "suggestions": [f"{self.name} suggestion"],
        }

    def get_specialization_info(self):  # pragma: no cover
        return {"name": self.name}


@pytest.mark.asyncio
async def test_path_memory_record_and_avoid() -> None:
    _paths.clear()
    mcp = DummyMCP()
    orchestrator = MultiAgentOrchestrator(mcp)
    orchestrator.specialists = {"code_review": DummySpecialist("code_review")}

    # First run should record a positive path
    result = await orchestrator.coordinate_specialists("please review this code")
    assert result["type"] == "single_specialist"
    assert _paths["project"]["positive"]

    # Record a negative path for the same specialists
    sig = PathSignature(
        steps=["code_review"],
        tools_used=["code_review"],
        key_decisions=[],
        metrics=Metrics(novelty=0.0, growth=0.0, cost=0.0),
        outcome=Outcome(result="fail"),
        scope="project",
    )
    record_path(PathRecord(actor="orchestrator", target="project", kind="negative", signature=sig))

    # Second run should be avoided due to negative memory
    result2 = await orchestrator.coordinate_specialists("please review this code")
    assert result2["type"] == "error"
    assert "Previously failed" in result2["coordination_summary"]
