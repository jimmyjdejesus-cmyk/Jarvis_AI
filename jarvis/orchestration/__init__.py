# Orchestration Package
"""
Multi-agent orchestration system for coordinating specialist AI agents

This package provides:
- MultiAgentOrchestrator: Coordinates multiple specialists for complex tasks
- SubOrchestrator: Scoped orchestrator used for nested missions
- Workflow management and task delegation
- Result synthesis and conflict resolution
This package provides building blocks for creating LangGraph based
orchestration workflows.  The previous specialised orchestrator has been
replaced by a small, generic template which can dynamically assemble graphs
from ``AgentSpec`` definitions.
"""

from importlib import import_module
from types import ModuleType
from typing import Any

__all__ = [
    "AgentSpec",
    "DynamicOrchestrator",
    "MultiAgentOrchestrator",
    "SubOrchestrator",
    "PathMemory",
    "MessageBus",
    "HierarchicalMessageBus",
    "Event",
    "BandwidthLimitedChannel",
    "MissionPlanner",
    "RedisTaskQueue",
    "END",
]


def __getattr__(name: str) -> Any:  # pragma: no cover - thin wrapper
    mapping = {
        "AgentSpec": (".orchestrator", "AgentSpec"),
        "DynamicOrchestrator": (".orchestrator", "DynamicOrchestrator"),
        "MultiAgentOrchestrator": (".orchestrator", "MultiAgentOrchestrator"),
        "END": (".orchestrator", "END"),
        "SubOrchestrator": (".sub_orchestrator", "SubOrchestrator"),
        "PruningManager": (".pruning", "PruningManager"),
        "PathMemory": (".path_memory", "PathMemory"),
        "MessageBus": (".message_bus", "MessageBus"),
        "HierarchicalMessageBus": (".message_bus", "HierarchicalMessageBus"),
        "Event": (".message_bus", "Event"),
        "BandwidthLimitedChannel": (".bandwidth_channel", "BandwidthLimitedChannel"),
        "MissionPlanner": (".mission_planner", "MissionPlanner"),
        "RedisTaskQueue": (".task_queue", "RedisTaskQueue"),
    }
    if name not in mapping:
        raise AttributeError(f"module 'jarvis.orchestration' has no attribute {name}")
    module_name, attr = mapping[name]
    module: ModuleType = import_module(module_name, __name__)
    value = getattr(module, attr)
    globals()[name] = value
    return value