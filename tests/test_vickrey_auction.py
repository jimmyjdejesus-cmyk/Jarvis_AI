import sys
sys.path.append(".")

from jarvis.scoring.vickrey_auction import Candidate, run_vickrey_auction


def test_vickrey_auction_basic():
    candidates = [
        Candidate(agent="a", bid=0.6, content="A"),
        Candidate(agent="b", bid=0.8, content="B"),
        Candidate(agent="c", bid=0.4, content="C"),
    ]
    result = run_vickrey_auction(candidates)
    assert result.winner.agent == "b"
    assert result.price == 0.6  # second highest bid
    assert result.metrics["diversity"] == 3
    assert round(result.metrics["avg_bid"], 2) == 0.6
