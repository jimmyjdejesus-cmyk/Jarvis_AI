from __future__ import annotations

import os
import sys
import types

# Mock neo4j to make tests runnable without the dependency
dummy_neo4j = types.SimpleNamespace(GraphDatabase=object, Driver=object)
sys.modules.setdefault("neo4j", dummy_neo4j)

sys.path.append(os.getcwd())

from jarvis.learning import PolicyOptimizer, RewardOracle, simulate
from jarvis.world_model.hypergraph import HierarchicalHypergraph


def test_scout_and_scholar_update_hypergraph():
    hypergraph = HierarchicalHypergraph()
    strategy_key = hypergraph.add_strategy(["step1"], confidence=0.2)
    rc = {"component": "db", "reason": "db correlated with failure"}
    neg_path = hypergraph.add_negative_pathway(strategy_key, rc)

    score_s, notes_s, diffs_s = simulate(
        {"type": "scout", "strategy_id": strategy_key}, hypergraph
    )
    assert "candidate" in diffs_s

    score_k, notes_k, diffs_k = simulate(
        {"type": "scholar", "neg_path_id": neg_path, "budget": 0.5}, hypergraph
    )
    assert "RCA" in notes_k
    assert diffs_k["budget"] <= 0.1

    oracle = RewardOracle()
    reward_s = oracle.score(score_s, diffs_s)
    reward_k = oracle.score(score_k, diffs_k)

    optimizer = PolicyOptimizer(hypergraph)
    optimizer.process_branch("scout", strategy_key, reward_s)
    optimizer.process_branch("scholar", strategy_key, reward_k, rca=diffs_k["rca"])

    layer2 = hypergraph.layers[2]
    assert any(d.get("mission") == "scout" for d in layer2.values())
    assert any(
        d.get("mission") == "scholar" and d.get("type") == "negative_pathway"
        for d in layer2.values()
    )

    layer3 = hypergraph.layers[3]
    assert any(n.get("mission") == "scholar" for n in layer3.values())


def test_scholar_budget_bounds():
    hypergraph = HierarchicalHypergraph()
    strategy_key = hypergraph.add_strategy(["step1"], confidence=0.2)
    rc = {"component": "db", "reason": "db correlated with failure"}
    neg_path = hypergraph.add_negative_pathway(strategy_key, rc)

    _, _, diffs_default = simulate(
        {"type": "scholar", "neg_path_id": neg_path}, hypergraph
    )
    assert diffs_default["budget"] == 0.1

    _, _, diffs_cap = simulate(
        {"type": "scholar", "neg_path_id": neg_path, "budget": 1.0}, hypergraph
    )
    assert diffs_cap["budget"] == 0.1

    _, _, diffs_neg = simulate(
        {"type": "scholar", "neg_path_id": neg_path, "budget": -0.5}, hypergraph
    )
    assert diffs_neg["budget"] == 0.0