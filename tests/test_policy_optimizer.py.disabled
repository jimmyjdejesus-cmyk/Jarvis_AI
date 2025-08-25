import os
import sys

sys.path.append(os.getcwd())

from jarvis.learning import PolicyOptimizer
from jarvis.world_model.hypergraph import HierarchicalHypergraph


def test_policy_optimizer_updates_strategy():
    hg = HierarchicalHypergraph()
    key = hg.add_strategy(["step"], confidence=0.2)
    opt = PolicyOptimizer(hg, learning_rate=0.5)
    opt.update_strategy(key, reward=1.0)
    node = hg.query(2, key)
    assert node is not None
    assert node["confidence"] > 0.2


def test_negative_pathway_created_on_failure():
    hg = HierarchicalHypergraph()
    key = hg.add_strategy(["step"], confidence=0.5, dependencies=["python<3.10"])
    opt = PolicyOptimizer(hg)
    opt.update_strategy(key, reward=0.0)
    neg = hg.query(2, f"{key}_neg")
    assert neg is not None
    assert neg["root_cause"]["component"] == "python<3.10"
