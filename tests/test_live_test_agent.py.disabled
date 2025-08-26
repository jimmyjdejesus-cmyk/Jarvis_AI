import sys
import os

sys.path.append(os.getcwd())

from jarvis.agents.live_test_agent import LiveTestAgent
from jarvis.learning import PolicyOptimizer
from jarvis.world_model.hypergraph import HierarchicalHypergraph


class DummyExecutive:
    def __init__(self, strategy_key):
        self.directives = []
        self.strategy_key = strategy_key

    def manage_directive(self, text):
        self.directives.append(text)
        return {"strategy_key": self.strategy_key, "output": "done"}


class DummyReward:
    def get_reward(self, query, response):
        return {"reward": 1.0}


def test_live_test_agent_processes_issue(monkeypatch):
    hg = HierarchicalHypergraph()
    key = hg.add_strategy(["fix"], confidence=0.1)
    exec_agent = DummyExecutive(key)
    reward_agent = DummyReward()
    optimizer = PolicyOptimizer(hg, learning_rate=0.5)

    issues = [{"number": 5, "title": "bug"}]

    def fake_list(repo):
        return issues

    monkeypatch.setattr("jarvis.tools.github.list_bug_issues", fake_list)

    agent = LiveTestAgent("owner/repo", exec_agent, reward_agent, optimizer)
    processed = agent.run_once()
    assert processed and exec_agent.directives
    node = hg.query(2, key)
    assert node["confidence"] > 0.1
