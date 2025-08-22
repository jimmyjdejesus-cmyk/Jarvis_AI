"""Autotuning utilities for resource budgeting and model selection.

This module provides:
- Budget and budget manager for tokens/time/CPU with dynamic reallocation.
- ModelSelector for choosing model/tool based on novelty and cost.
- MetricsEmitter for emitting operational metrics.
- AutotuneManager that coordinates policies and budgeting.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple


class PolicyType(str, Enum):
    """Available autotuning policies."""

    AGGRESSIVE = "aggressive"
    BALANCED = "balanced"
    CONSERVATIVE = "conservative"


@dataclass
class Budget:
    """Execution budget for a single task."""

    tokens: int
    time_sec: float
    cpu_sec: float

    def consume(self, tokens: int, time_sec: float, cpu_sec: float) -> None:
        """Consume part of the budget."""
        self.tokens = max(self.tokens - tokens, 0)
        self.time_sec = max(self.time_sec - time_sec, 0.0)
        self.cpu_sec = max(self.cpu_sec - cpu_sec, 0.0)

    def exhausted(self) -> bool:
        """Return True if any component of the budget is exhausted."""
        return self.tokens <= 0 or self.time_sec <= 0.0 or self.cpu_sec <= 0.0


@dataclass
class TeamState:
    """State for tracking team growth and allocated budget."""

    budget: Budget
    growth: float = 1.0


class BudgetManager:
    """Manage budgets across teams with dynamic reallocation."""

    def __init__(self, default_budget: Budget):
        self.default_budget = default_budget
        self.teams: Dict[str, TeamState] = {}

    def register_team(self, team_id: str, growth: float = 1.0) -> None:
        if team_id not in self.teams:
            self.teams[team_id] = TeamState(
                budget=Budget(
                    tokens=self.default_budget.tokens,
                    time_sec=self.default_budget.time_sec,
                    cpu_sec=self.default_budget.cpu_sec,
                ),
                growth=growth,
            )

    def allocate(self, team_id: str) -> Budget:
        """Get current budget for a team, creating if necessary."""
        self.register_team(team_id)
        return self.teams[team_id].budget

    def update_growth(self, team_id: str, growth: float) -> None:
        self.register_team(team_id, growth)
        self.teams[team_id].growth = growth
        self._rebalance()

    def _rebalance(self) -> None:
        """Reallocate budgets so high-growth teams receive extra share."""
        total_growth = sum(team.growth for team in self.teams.values()) or 1.0
        for team in self.teams.values():
            ratio = team.growth / total_growth
            team.budget.tokens = int(self.default_budget.tokens * ratio)
            team.budget.time_sec = self.default_budget.time_sec * ratio
            team.budget.cpu_sec = self.default_budget.cpu_sec * ratio


class ModelSelector:
    """Select models or tools based on novelty and cost metrics."""

    def select(self, novelty: float, cost: float) -> str:
        """Return model policy string."""
        if novelty < 0.2 and cost > 0.8:
            return "prune"
        if novelty >= 0.7 and cost <= 0.3:
            return "heavy"
        if novelty < 0.4 and cost > 0.6:
            return "light"
        return "standard"


@dataclass
class TeamCycleMetrics:
    tokens: int
    latency_ms: float
    cost_est: float
    growth: float


class MetricsEmitter:
    """Simple in-memory metrics pipeline."""

    def __init__(self):
        self.team_cycles: Dict[str, List[TeamCycleMetrics]] = {}
        self.prune_rates: List[float] = []
        self.merge_latencies: List[float] = []
        self.novelty_distribution: List[float] = []

    def emit_team_cycle(self, team_id: str, tokens: int, latency_ms: float, cost_est: float, growth: float) -> None:
        metrics = TeamCycleMetrics(tokens, latency_ms, cost_est, growth)
        self.team_cycles.setdefault(team_id, []).append(metrics)

    def emit_prune_rate(self, rate: float) -> None:
        self.prune_rates.append(rate)

    def emit_merge_latency(self, latency_ms: float) -> None:
        self.merge_latencies.append(latency_ms)

    def emit_novelty_distribution(self, novelty: float) -> None:
        self.novelty_distribution.append(novelty)


class AutotuneManager:
    """Coordinate budgeting, model selection and policies."""

    def __init__(self, policy: PolicyType = PolicyType.BALANCED):
        self.policy = policy
        base_budget = self._policy_budget(policy)
        self.budgets = BudgetManager(base_budget)
        self.selector = ModelSelector()
        self.metrics = MetricsEmitter()

    def _policy_budget(self, policy: PolicyType) -> Budget:
        if policy == PolicyType.AGGRESSIVE:
            return Budget(tokens=2000, time_sec=60.0, cpu_sec=60.0)
        if policy == PolicyType.CONSERVATIVE:
            return Budget(tokens=500, time_sec=20.0, cpu_sec=20.0)
        return Budget(tokens=1000, time_sec=40.0, cpu_sec=40.0)

    def optimize_tokens(self, baseline: int) -> Tuple[int, int]:
        """Return baseline vs optimized tokens under policy."""
        if self.policy == PolicyType.BALANCED:
            optimized = int(baseline * 0.75)
        elif self.policy == PolicyType.AGGRESSIVE:
            optimized = int(baseline * 0.6)
        else:
            optimized = int(baseline * 0.9)
        return baseline, optimized


__all__ = [
    "PolicyType",
    "Budget",
    "BudgetManager",
    "ModelSelector",
    "MetricsEmitter",
    "AutotuneManager",
]

