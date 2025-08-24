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

# Optional specialist agents – failure to import simply leaves them as ``None``
try:  # pragma: no cover
    from .coding_agent import CodingAgent, get_coding_agent
except Exception:  # pragma: no cover
    CodingAgent = None  # type: ignore

    def get_coding_agent(*_args, **_kwargs):  # type: ignore
        raise ImportError("CodingAgent not available")

try:  # pragma: no cover
    from .simulation_agent import SimulationAgent
except Exception:  # pragma: no cover
    SimulationAgent = None  # type: ignore

try:  # pragma: no cover
    from .monte_carlo_explorer import MonteCarloExplorer
except Exception:  # pragma: no cover
    MonteCarloExplorer = None  # type: ignore

try:  # pragma: no cover
    from .benchmark_agent import BenchmarkRewardAgent
except Exception:  # pragma: no cover
    BenchmarkRewardAgent = None  # type: ignore

try:  # pragma: no cover
    from .live_test_agent import LiveTestAgent
except Exception:  # pragma: no cover
    LiveTestAgent = None  # type: ignore

__all__ = [
    "CodingAgent",
    "get_coding_agent",
    "MissionPlanner",
    "CuriosityAgent",
    "SimulationAgent",
    "MonteCarloExplorer",
    "BenchmarkRewardAgent",
    "LiveTestAgent",
]

