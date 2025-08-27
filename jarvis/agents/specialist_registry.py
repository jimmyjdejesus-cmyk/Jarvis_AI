"""Factory and registry for specialist agents."""
from __future__ import annotations

from typing import Any, Dict, Type

from .specialist import SpecialistAgent
from .domain_specialists import (
    DocumentationSpecialist,
    DatabaseSpecialist,
    SecuritySpecialist,
    LocalizationSpecialist,
)
from .specialists import (
    CodeReviewAgent,
    ArchitectureAgent,
    TestingAgent,
    DevOpsAgent,
    CloudCostOptimizerAgent,
    UserFeedbackAgent,
)

SPECIALIST_REGISTRY: Dict[str, Type[SpecialistAgent]] = {
    "docs": DocumentationSpecialist,
    "database": DatabaseSpecialist,
    "security": SecuritySpecialist,
    "localization": LocalizationSpecialist,
    "code_review": CodeReviewAgent,
    "architecture": ArchitectureAgent,
    "testing": TestingAgent,
    "devops": DevOpsAgent,
    "cloud_cost": CloudCostOptimizerAgent,
    "user_feedback": UserFeedbackAgent,
}


def create_specialist(name: str, mcp_client: Any, **kwargs) -> SpecialistAgent:
    """Instantiate a specialist by name."""
    cls = SPECIALIST_REGISTRY.get(name)
    if cls is None:
        raise KeyError(f"Unknown specialist: {name}")
    return cls(mcp_client=mcp_client, **kwargs)
