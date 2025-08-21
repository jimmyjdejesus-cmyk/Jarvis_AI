"""Jarvis AI Ecosystem utilities.

This lightweight __init__ exposes only the minimal components required for
internal tests to avoid heavy optional dependencies."""

try:
    from .meta_intelligence import MetaAgent, SpecialistAIAgent, AgentCapability, SystemHealth
except Exception:  # pragma: no cover
    MetaAgent = None
    SpecialistAIAgent = None
    AgentCapability = None
    SystemHealth = None

__all__ = [
    "MetaAgent",
    "SpecialistAIAgent",
    "AgentCapability",
    "SystemHealth",
]

"""Minimal ecosystem package for tests."""

from .meta_intelligence import MetaAgent

__all__ = ["MetaAgent"]

