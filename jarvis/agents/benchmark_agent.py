from __future__ import annotations

"""Agent that evaluates responses against benchmark answers.

This specialist provides a quantitative reward for exact‑match benchmarking
and records token usage for efficiency comparisons.
"""

import json
from typing import Any, Dict, List, Optional

from jarvis.agents.base_specialist import BaseSpecialist


class BenchmarkRewardAgent(BaseSpecialist):
    """Score generated responses against a benchmark dataset."""

    def __init__(self, mcp_client, benchmark_file: str) -> None:
        self.mcp_client = mcp_client
        with open(benchmark_file, "r", encoding="utf-8") as f:
            self.benchmarks = json.load(f)
        self.specialization = "Provides a reward score for benchmark tasks."

    def get_reward(self, query: str, generated_response: str) -> Dict[str, Any]:
        """Return a reward and token count for the given query."""
        golden_answer = self.benchmarks.get(query)
        token_count = len(generated_response.split())  # Simple tokenization for demo

        if not golden_answer:
            return {
                "reward": 0.0,
                "tokens": token_count,
                "error": "Query not in benchmark.",
            }

        is_match = golden_answer.lower() in generated_response.lower()
        reward = 1.0 if is_match else 0.0

        print(
            f"BENCHMARK: Query='{query[:30]}...' | Match={is_match} | Tokens={token_count}"
        )
        return {"reward": reward, "tokens": token_count}

    async def process_task(
        self,
        task: str,
        context: Optional[List[Dict[str, Any]]] = None,
        user_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """This agent does not support direct task processing."""
        raise NotImplementedError(
            "BenchmarkRewardAgent is intended only for reward computation."
        )

    def get_specialization_info(self) -> Dict[str, Any]:
        """Return specialization metadata."""
        return {"specialization": self.specialization}


__all__ = ["BenchmarkRewardAgent"]
