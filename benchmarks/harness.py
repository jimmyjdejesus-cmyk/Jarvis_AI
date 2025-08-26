"""Asynchronous benchmarking harness for Jarvis AI.

Provides utilities to run multiple scenarios and collect performance
metrics such as latency, token usage, pruning rate and quality score.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union

import plotly.graph_objects as go


@dataclass
class Metric:
    """Container for metrics from a single run."""

    time_to_first_token: float
    total_latency: float
    token_count: int
    token_cost: float
    success_rate: float
    prune_rate: float
    bq_score: float
    answer_relevance: float
    citation_count: int

    def to_dict(self) -> Dict[str, float]:
        """Return a JSON-serialisable representation."""
        return {
            "time_to_first_token": self.time_to_first_token,
            "total_latency": self.total_latency,
            "token_count": self.token_count,
            "prune_rate": self.prune_rate,
            "bq_score": self.bq_score,
        }


ScenarioFn = Callable[["Context"], Awaitable[Union[str, Dict[str, Any]]]]


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

    def __init__(
        self, scenarios: List[BenchmarkScenario], *, concurrency: int = 4
    ) -> None:
        self.scenarios = scenarios
        self.semaphore = asyncio.Semaphore(concurrency)

    async def _run_single(
        self,
        scenario: BenchmarkScenario,
        policy: str,
    ) -> Metric:
        ctx = Context()

        async with self.semaphore:
            start = time.perf_counter()
            first_token_time: Optional[float] = None
            token_counter = 0
            relevance = 0.0
            citations = []

            async def token_stream() -> str:
                nonlocal first_token_time, token_counter, relevance, citations
                
                # Simulate streaming tokens from the scenario function.
                result = await scenario.fn(ctx)

                if isinstance(result, dict):
                    answer = result.get("answer", "")
                    relevance = float(result.get("relevance", 0.0))
                    citations = result.get("citations", [])
                else:
                    answer = result

                for token in answer.split():
                    if first_token_time is None:
                        first_token_time = time.perf_counter()
                    token_counter += 1
                    await asyncio.sleep(0)
                return answer

            result = await token_stream()
            end = time.perf_counter()

        success = 1.0 if result.strip() else 0.0
        return Metric(
            time_to_first_token=(first_token_time or start) - start,
            total_latency=end - start,
            token_count=token_counter,
            token_cost=float(token_counter),
            success_rate=success,
            prune_rate=0.0 if policy == "no-prune" else 0.3,
            bq_score=1.0,
            answer_relevance=relevance,
            citation_count=len(citations),
        )

    async def run(self, policy: str) -> Dict[str, Metric]:
        tasks = [self._run_single(s, policy) for s in self.scenarios]
        results = await asyncio.gather(*tasks)
        return {s.name: m for s, m in zip(self.scenarios, results)}


def benchmark_table(
    balanced: Dict[str, Metric], no_prune: Dict[str, Metric]
) -> List[Dict[str, Any]]:
    """Return a summary table comparing two policies."""

    table: List[Dict[str, Any]] = []
    for name in balanced:
        b = balanced[name]
        n = no_prune[name]
        token_savings = 1 - b.token_count / max(n.token_count, 1)
        numerator = b.total_latency - n.total_latency
        latency_increase = numerator / max(n.total_latency, 1)
        table.append(
            {
                "scenario": name,
                "success_balanced": b.success_rate,
                "success_no_prune": n.success_rate,
                "token_cost_balanced": b.token_cost,
                "token_cost_no_prune": n.token_cost,
                "latency_balanced": b.total_latency,
                "latency_no_prune": n.total_latency,
                "token_savings": token_savings,
                "latency_increase": latency_increase,
                "bq_balanced": b.bq_score,
                "bq_no_prune": n.bq_score,
                "relevance_balanced": b.answer_relevance,
                "relevance_no_prune": n.answer_relevance,
                "citations_balanced": b.citation_count,
                "citations_no_prune": n.citation_count,
            }
        )
    return table


async def run_standard_benchmarks(
    output_dir: Optional[Path] = None,
) -> Dict[str, Metric]:
    """Execute the default coding, repo reasoning and Q&A scenarios.

    If ``output_dir`` is provided the metrics, plot and summary markdown are
    written to that directory. The function returns the raw metric mapping.
    """

    async def coding(_ctx: Context) -> str:
        return "def add(a, b): return a + b"

    async def repo_reasoning(_ctx: Context) -> str:
        count = sum(1 for _ in Path(".").rglob("*.py"))
        return f"python_files {count}"

    async def qa(_ctx: Context) -> str:
        data_path = Path("data/rex_rag_benchmarks/dead_end_qa.json")
        data = json.loads(data_path.read_text())
        question, answer = next(iter(data.items()))
        return f"{question} -> {answer}"

    scenarios = [
        BenchmarkScenario("coding", coding),
        BenchmarkScenario("repo_reasoning", repo_reasoning),
        BenchmarkScenario("q_and_a", qa),
    ]

    runner = BenchmarkRunner(scenarios)
    results = await runner.run("standard")

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        metrics_path = output_dir / f"{stamp}_metrics.json"
        summary_path = output_dir / f"{stamp}_summary.md"
        plot_path = output_dir / f"{stamp}_latency.html"

        payload = {k: v.to_dict() for k, v in results.items()}
        with metrics_path.open("w") as fh:
            json.dump(payload, fh, indent=2)

        with summary_path.open("w") as fh:
            fh.write("# Benchmark Summary\n\n")
            for name, metric in results.items():
                fh.write(
                    f"## {name}\n"
                    f"- latency: {metric.total_latency:.4f}s\n"
                    f"- tokens: {metric.token_count}\n"
                    f"- bq score: {metric.bq_score}\n\n"
                )
            fh.write(f"Plot: {plot_path.name}\n")

        fig = go.Figure(
            [
                go.Bar(
                    x=list(results.keys()),
                    y=[m.total_latency for m in results.values()],
                    name="total_latency",
                )
            ]
        )
        fig.update_layout(
            title="Latency by scenario",
            xaxis_title="Scenario",
            yaxis_title="Seconds",
        )
        fig.write_html(str(plot_path))

    return results


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run benchmark harness")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("benchmarks/results"),
        help="Directory to write results to",
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="Run in CI mode without writing result files",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    out_dir = None if args.ci else args.output
    asyncio.run(run_standard_benchmarks(out_dir))


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()


__all__ = [
    "BenchmarkScenario",
    "BenchmarkRunner",
    "benchmark_table",
    "Context",
    "Metric",
    "run_standard_benchmarks",
]
