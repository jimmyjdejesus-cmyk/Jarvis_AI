"""
Multi-agent orchestration system for coordinating specialist AI agents.
"""
from .orchestrator import (
    AgentSpec,
    DynamicOrchestrator,
    MultiAgentOrchestrator,
    OrchestratorTemplate,
    StepContext,
    StepResult,
    END,
)
try:  # pragma: no cover - optional import
    from .sub_orchestrator import SubOrchestrator
except Exception:  # pragma: no cover
    SubOrchestrator = None  # type: ignore
from .path_memory import PathMemory
from .message_bus import MessageBus, HierarchicalMessageBus, Event
from .bandwidth_channel import BandwidthLimitedChannel
try:  # pragma: no cover - optional dependencies
    from .mission_planner import MissionPlanner
except Exception:  # pragma: no cover
    MissionPlanner = None  # type: ignore
try:
    from .task_queue import RedisTaskQueue
except Exception:  # pragma: no cover
    RedisTaskQueue = None  # type: ignore
try:
    from .pruning import PruningManager
except Exception:  # pragma: no cover
    PruningManager = None  # type: ignore
try:
    from .server import app, bus
except Exception:  # pragma: no cover
    app = None  # type: ignore
    bus = None  # type: ignore
from .crews import CodeAuditCrew, ResearchCrew

__all__ = [
    "AgentSpec",
    "DynamicOrchestrator",
    "MultiAgentOrchestrator",
    "OrchestratorTemplate",
    "StepContext",
    "StepResult",
    "SubOrchestrator",
    "PathMemory",
    "MessageBus",
    "HierarchicalMessageBus",
    "Event",
    "BandwidthLimitedChannel",
    "MissionPlanner",
    "RedisTaskQueue",
    "PruningManager",
    "CodeAuditCrew",
    "ResearchCrew",
    "END",
    "app",
    "bus",
]