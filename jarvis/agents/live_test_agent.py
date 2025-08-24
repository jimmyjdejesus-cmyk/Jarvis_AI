from __future__ import annotations

"""Agent that monitors GitHub issues and feeds directives to the ExecutiveAgent."""

from typing import List, Dict, Any, TYPE_CHECKING
import time

from jarvis.tools import github

if TYPE_CHECKING:  # pragma: no cover - import for type checking only
    from jarvis.agents.benchmark_agent import BenchmarkRewardAgent
    from jarvis.ecosystem.meta_intelligence import ExecutiveAgent
    from jarvis.learning.policy_optimizer import PolicyOptimizer


class LiveTestAgent:
    """Poll GitHub for new bug reports and trigger bug-fix directives."""

    def __init__(
        self,
        repo: str,
        executive: "ExecutiveAgent",
        reward_agent: "BenchmarkRewardAgent",
        policy_optimizer: "PolicyOptimizer",
        poll_interval: int = 60,
    ) -> None:
        self.repo = repo
        self.executive = executive
        self.reward_agent = reward_agent
        self.policy_optimizer = policy_optimizer
        self.poll_interval = poll_interval
        self.processed: set[int] = set()

    def fetch_new_bug_reports(self) -> List[Dict[str, Any]]:
        """Return unprocessed bug issues."""
        issues = github.list_bug_issues(self.repo)
        return [i for i in issues if i["number"] not in self.processed]

    def handle_issue(self, issue: Dict[str, Any]) -> None:
        """Convert a GitHub issue into an executive directive and learn from the outcome."""
        directive = (
            f"Analyze, reproduce, and fix the bug described in Issue #{issue['number']}."
        )
        result = self.executive.manage_directive(directive)
        reward = self.reward_agent.get_reward(issue.get("title", ""), result.get("output", ""))
        strategy_key = result.get("strategy_key")
        if strategy_key is not None:
            self.policy_optimizer.update_strategy(strategy_key, reward.get("reward", 0.0))
        self.processed.add(issue["number"])

    def run_once(self) -> List[Dict[str, Any]]:
        """Check for new issues and process them once."""
        new_issues = self.fetch_new_bug_reports()
        for issue in new_issues:
            self.handle_issue(issue)
        return new_issues

    def run(self) -> None:
        """Continuously poll for new bug reports."""
        while True:
            self.run_once()
            time.sleep(self.poll_interval)
