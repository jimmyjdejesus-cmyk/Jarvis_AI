import math

from jarvis.pruning import PruningEvaluator, path_signature


def dummy_embed(text: str):
    # simple embedding: counts of characters
    return [float(len(text)), float(sum(ord(c) for c in text) % 100), 1.0]


def test_pruning_evaluator_scoring():
    evaluator = PruningEvaluator(dummy_embed, {"window": 3})
    team_outputs = ["alpha", "beta", "gamma"]
    other_outputs = ["alpha", "beta", "delta"]
    scores = evaluator.score(team_outputs, other_outputs, [0.1, 0.2], 500)
    assert 0.0 <= scores["novelty"] <= 1.0
    assert math.isclose(scores["growth"], 0.1, rel_tol=1e-5)
    assert scores["cost_gain"] > 0


def test_path_signature_deterministic():
    sig1 = path_signature(["s1", "s2"], ["t1"], ["d1"])
    sig2 = path_signature(["s1", "s2"], ["t1"], ["d1"])
    assert sig1 == sig2
    assert "hash" in sig1
