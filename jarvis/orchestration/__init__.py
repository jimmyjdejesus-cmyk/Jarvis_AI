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
from .path_memory import PathMemory
from .message_bus import MessageBus, HierarchicalMessageBus, Event
from .bandwidth_channel import BandwidthLimitedChannel

# Adopt the safer optional import style from main for all components
try:  # pragma: no cover - optional import
    from .sub_orchestrator import SubOrchestrator
except Exception:  # pragma: no cover
    SubOrchestrator = None  # type: ignore

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

# Add the new SemanticCache from the feature branch, also as an optional import
try:
    from .semantic_cache import SemanticCache
except Exception:  # pragma: no cover
    SemanticCache = None  # type: ignore

try:
    from .server import app, bus
except Exception:  # pragma: no cover
    app = None  # type: ignore
    bus = None  # type: ignore

# Add the new Crews from the main branch
try:
    from .crews import CodeAuditCrew, ResearchCrew
except Exception:  # pragma: no cover
    CodeAuditCrew = None  # type: ignore
    ResearchCrew = None  # type: ignore


# Combine __all__ to include everything from both branches
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
    "SemanticCache",      # From feature branch
    "CodeAuditCrew",      # From main branch
    "ResearchCrew",       # From main branch
    "END",
    "app",
    "bus",
]