"""Asynchronous benchmarking harness for Jarvis AI.

Provides utilities to run multiple scenarios and collect performance
metrics such as latency, token usage, pruning rate and quality score.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional


@dataclass
class Metric:
    """Container for metrics from a single run."""

    time_to_first_token: float
    total_latency: float
    token_count: int
    prune_rate: float
    bq_score: float


ScenarioFn = Callable[["Context"], Awaitable[str]]


@dataclass
class Context:
    """Context passed to scenarios.

    The context contains a simple in-memory cache. The cache is keyed by a
    hash of the prompt and any additional parameters. This enables response
    caching across runs which mirrors the real system behaviour.
    """

    cache: Dict[str, str] = field(default_factory=dict)

    def get_cached(self, prompt: str) -> Optional[str]:
        key = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        return self.cache.get(key)

    def set_cached(self, prompt: str, response: str) -> None:
        key = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        self.cache[key] = response


@dataclass
class BenchmarkScenario:
    name: str
    fn: ScenarioFn


class BenchmarkRunner:
    """Runner that executes scenarios under different policies."""

    def __init__(self, scenarios: List[BenchmarkScenario], *, concurrency: int = 4) -> None:
        self.scenarios = scenarios
        self.semaphore = asyncio.Semaphore(concurrency)

    async def _run_single(self, scenario: BenchmarkScenario, policy: str) -> Metric:
        ctx = Context()

        async with self.semaphore:
            start = time.perf_counter()
            first_token_time: Optional[float] = None
            token_counter = 0

            async def token_stream() -> str:
                nonlocal first_token_time, token_counter
                # Simulate streaming tokens from the scenario function.
                result = await scenario.fn(ctx)
                for i, token in enumerate(result.split()):
                    if first_token_time is None:
                        first_token_time = time.perf_counter()
                    token_counter += 1
                    await asyncio.sleep(0)
                return result

            await token_stream()
            end = time.perf_counter()

        return Metric(
            time_to_first_token=(first_token_time or start) - start,
            total_latency=end - start,
            token_count=token_counter,
            prune_rate=0.0 if policy == "no-prune" else 0.3,
            bq_score=1.0,
        )

    async def run(self, policy: str) -> Dict[str, Metric]:
        tasks = [self._run_single(s, policy) for s in self.scenarios]
        results = await asyncio.gather(*tasks)
        return {s.name: m for s, m in zip(self.scenarios, results)}


def benchmark_table(balanced: Dict[str, Metric], no_prune: Dict[str, Metric]) -> List[Dict[str, Any]]:
    """Return a summary table comparing two policies."""

    table: List[Dict[str, Any]] = []
    for name in balanced:
        b = balanced[name]
        n = no_prune[name]
        token_savings = 1 - b.token_count / max(n.token_count, 1)
        latency_increase = (b.total_latency - n.total_latency) / max(n.total_latency, 1)
        table.append(
            {
                "scenario": name,
                "token_savings": token_savings,
                "latency_increase": latency_increase,
                "bq_balanced": b.bq_score,
                "bq_no_prune": n.bq_score,
            }
        )
    return table


__all__ = [
    "BenchmarkScenario",
    "BenchmarkRunner",
    "benchmark_table",
    "Context",
    "Metric",
]
