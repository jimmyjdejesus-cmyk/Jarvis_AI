import asyncio
from typing import Dict

import pytest



class MockSpecialist:
    """Lightweight specialist for backend coordination tests."""

    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    async def process_task(self, task: str, **kwargs) -> Dict[str, str]:
        await asyncio.sleep(0.01)
        return {"specialist": self.name, "response": f"{self.role} analysis"}


class MockOrchestrator:
    """Mock orchestrator mirroring backend specialist selection logic."""

    def __init__(self):
        self.specialists = {
            "security": MockSpecialist("security", "Security"),
            "architecture": MockSpecialist("architecture", "Architecture"),
            "code_review": MockSpecialist("code_review", "Code Review"),
            "testing": MockSpecialist("testing", "Testing"),
            "devops": MockSpecialist("devops", "DevOps"),
            "research": MockSpecialist("research", "Research"),
        }

    async def coordinate_specialists(self, request: str, **kwargs) -> Dict[str, any]:
        request_lower = request.lower()
        specialists_used = []
        if "security" in request_lower:
            specialists_used.append("security")
        if "architecture" in request_lower or "design" in request_lower:
            specialists_used.append("architecture")
        if "test" in request_lower:
            specialists_used.append("testing")
        if "review" in request_lower:
            specialists_used.append("code_review")
        if "deploy" in request_lower:
            specialists_used.append("devops")
        if "research" in request_lower or not specialists_used:
            specialists_used.append("research")
        results = {}
        for name in specialists_used:
            results[name] = await self.specialists[name].process_task(request)
        return {
            "type": "orchestrated_response",
            "complexity": "medium",
            "specialists_used": specialists_used,
            "results": results,
            "synthesized_response": f"Coordinated analysis from {len(specialists_used)} specialists for: {request}",
            "confidence": 0.85,
            "coordination_summary": f"Successfully coordinated {len(specialists_used)} specialists",
        }


@pytest.fixture()
def cerebro() -> MockOrchestrator:
    """Return a fresh mock orchestrator for each test."""
    return MockOrchestrator()


@pytest.mark.asyncio
async def test_coordinate_specialists_success(cerebro: MockOrchestrator):
    """Cerebro uses expected specialists and returns a synthesized response."""
    result = await cerebro.coordinate_specialists(
        "Test security analysis of authentication system"
    )
    assert result["specialists_used"] == ["security", "testing"]
    assert "Coordinated analysis from 2 specialists" in result["synthesized_response"]
    assert "authentication system" in result["synthesized_response"]
    assert result["type"] == "orchestrated_response"
    assert not result.get("error")


@pytest.mark.asyncio
async def test_coordinate_specialists_invalid_request(cerebro: MockOrchestrator):
    """Invalid request types should raise an error."""
    with pytest.raises(AttributeError):
        await cerebro.coordinate_specialists(None)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_specialist_failure_raises(cerebro: MockOrchestrator, monkeypatch):
    """Specialist processing errors propagate to the caller."""

    async def boom(task: str, **kwargs):  # pragma: no cover - demonstration
        raise RuntimeError("boom")

    monkeypatch.setattr(cerebro.specialists["security"], "process_task", boom)
    with pytest.raises(RuntimeError):
        await cerebro.coordinate_specialists("Security review")
