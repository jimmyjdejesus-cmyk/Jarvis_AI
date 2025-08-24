"""Orchestration package providing mission planning and agent coordination."""

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