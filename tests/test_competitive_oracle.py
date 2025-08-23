import pytest
import sys
from importlib import util
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
spec = util.spec_from_file_location(
    "graph", Path(__file__).resolve().parents[1] / "jarvis" / "orchestration" / "graph.py"
)
graph = util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(graph)
MultiTeamOrchestrator = graph.MultiTeamOrchestrator


def test_oracle_selects_higher_score():
    result = MultiTeamOrchestrator._oracle_judge({"quality": 0.9}, {"quality": 0.3})
    assert result["winner"] == "Yellow"
    assert result["scores"]["Yellow"] > result["scores"]["Green"]


def test_oracle_fallback_to_length():
    yellow = {"research_summary": "abc"}
    green = {"research_summary": "a"}
    result = MultiTeamOrchestrator._oracle_judge(yellow, green)
    assert result["winner"] == "Yellow"

