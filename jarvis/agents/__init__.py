"""Lightweight agents package used in tests.

Only a small subset of the full project agents are exposed here with guarded
imports to avoid heavy optional dependencies during testing.
"""

from __future__ import annotations

# Core planning and curiosity utilities
try:  # pragma: no cover - optional dependencies
    from .mission_planner import MissionPlanner
except Exception:  # pragma: no cover
    MissionPlanner = None  # type: ignore

try:  # pragma: no cover - optional dependencies
    from .curiosity_agent import CuriosityAgent
except Exception:  # pragma: no cover
    CuriosityAgent = None  # type: ignore

# Optional curiosity question routing
try:  # pragma: no cover - optional dependencies
    from .curiosity_router import CuriosityRouter
except (ImportError, SyntaxError):  # pragma: no cover
    CuriosityRouter = None  # type: ignore

# Optional specialist agents – failure to import simply leaves them as ``None``
try:  # pragma: no cover
    from .coding_agent import CodingAgent, get_coding_agent
except (ImportError, SyntaxError):  # pragma: no cover
    CodingAgent = None  # type: ignore

from .base_specialist import BaseSpecialist
try:  # pragma: no cover - optional dependencies
    from .simulation_agent import SimulationAgent
    from .monte_carlo_explorer import MonteCarloExplorer
    from .benchmark_agent import BenchmarkRewardAgent
    from .decentralized_actor import DecentralizedActor
except (ImportError, SyntaxError):  # pragma: no cover
    SimulationAgent = None  # type: ignore
    MonteCarloExplorer = None  # type: ignore
    BenchmarkRewardAgent = None  # type: ignore
    DecentralizedActor = None  # type: ignore

try:
    from .live_test_agent import LiveTestAgent  # noqa: F401
except Exception:  # pragma: no cover
    LiveTestAgent = None  # type: ignore