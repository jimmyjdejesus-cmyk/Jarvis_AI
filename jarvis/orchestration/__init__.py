"""
Multi-agent orchestration system for coordinating specialist AI agents.
"""
try:  # pragma: no cover - optional import
    from .orchestrator import (
        AgentSpec,
        DynamicOrchestrator,
        MultiAgentOrchestrator,
        OrchestratorTemplate,
        StepContext,
        StepResult,
        END,
    )
except (ImportError, ModuleNotFoundError):  # pragma: no cover
    AgentSpec = None  # type: ignore
    DynamicOrchestrator = None  # type: ignore
    MultiAgentOrchestrator = None  # type: ignore
    OrchestratorTemplate = None  # type: ignore
    StepContext = None  # type: ignore
    StepResult = None  # type: ignore
    END = None  # type: ignore

from .path_memory import PathMemory
from .message_bus import MessageBus, HierarchicalMessageBus, Event
from .bandwidth_channel import BandwidthLimitedChannel

# Some optional orchestrator variants depend on experimental ecosystem modules
# that may not be available in all environments. Import defensively.
try:  # pragma: no cover - optional import
    from .black_team_orchestrator import BlackTeamOrchestrator
except Exception:  # pragma: no cover
    BlackTeamOrchestrator = None  # type: ignore

# Optional imports for extended functionality
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

try:
    from .semantic_cache import SemanticCache
except Exception:  # pragma: no cover
    SemanticCache = None  # type: ignore

try:
    from .server import app, bus
except Exception:  # pragma: no cover
    app = None  # type: ignore
    bus = None  # type: ignore

try:
    from .crews import CodeAuditCrew, ResearchCrew
except Exception:  # pragma: no cover
    CodeAuditCrew = None  # type: ignore
    ResearchCrew = None  # type: ignore


# Combined __all__ list including additions from both branches
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
    "BlackTeamOrchestrator",
    "MissionPlanner",
    "RedisTaskQueue",
    "PruningManager",
    "SemanticCache",
    "CodeAuditCrew",
    "ResearchCrew",
    "END",
    "app",
    "bus",
]
