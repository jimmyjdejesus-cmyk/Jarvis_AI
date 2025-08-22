import sys
import pathlib
import pytest

# Ensure project root is on sys.path
sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent))

from jarvis.core.autotune import (
    AutotuneManager,
    PolicyType,
    Budget,
    BudgetManager,
    ModelSelector,
    MetricsEmitter,
)


def test_model_selector_behavior():
    selector = ModelSelector()
    assert selector.select(0.8, 0.2) == "heavy"
    assert selector.select(0.3, 0.7) == "light"
    assert selector.select(0.1, 0.9) == "prune"
    assert selector.select(0.5, 0.5) == "standard"


def test_budget_rebalancing():
    manager = BudgetManager(Budget(tokens=100, time_sec=10.0, cpu_sec=10.0))
    manager.register_team("alpha", growth=1.0)
    manager.register_team("beta", growth=1.0)
    manager.update_growth("alpha", 3.0)
    alpha_budget = manager.allocate("alpha")
    beta_budget = manager.allocate("beta")
    assert alpha_budget.tokens > beta_budget.tokens


def test_metrics_emitter():
    metrics = MetricsEmitter()
    metrics.emit_team_cycle("team1", 100, 200.0, 1.5, 1.2)
    metrics.emit_prune_rate(0.1)
    metrics.emit_merge_latency(50.0)
    metrics.emit_novelty_distribution(0.7)
    assert "team1" in metrics.team_cycles
    assert metrics.prune_rates == [0.1]
    assert metrics.merge_latencies == [50.0]
    assert metrics.novelty_distribution == [0.7]


def test_balanced_policy_reduces_tokens():
    manager = AutotuneManager(PolicyType.BALANCED)
    baseline, optimized = manager.optimize_tokens(1000)
    assert baseline == 1000
    assert optimized <= 750
