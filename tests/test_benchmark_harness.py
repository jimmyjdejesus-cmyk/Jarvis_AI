import asyncio
import sys
from pathlib import Path

# Ensure repository root on path for direct test invocation
sys.path.append(str(Path(__file__).resolve().parents[1]))

from benchmarks.harness import (  # noqa: E402
    run_standard_benchmarks,
    BenchmarkRunner,
    BenchmarkScenario,
    benchmark_table,
)


async def dummy_scenario(context):
    """Simulate a simple scenario for benchmark testing."""
    # Simulate some response; using caching to test functionality
    cached = context.get_cached("prompt")
    if cached:
        return cached
    context.set_cached("prompt", "ok")
    await asyncio.sleep(0)
    return "ok"


def test_runner_collects_metrics():
    """Verify that the BenchmarkRunner correctly collects and processes metrics."""
    runner = BenchmarkRunner([BenchmarkScenario("dummy", dummy_scenario)])
    balanced = asyncio.run(runner.run("balanced"))
    no_prune = asyncio.run(runner.run("no-prune"))
    table = benchmark_table(balanced, no_prune)
    assert table[0]["scenario"] == "dummy"
    assert 0 <= table[0]["token_savings"] <= 1
    assert table[0]["success_balanced"] == 1.0
    assert table[0]["token_cost_no_prune"] >= 0


def test_run_standard_benchmarks(tmp_path: Path) -> None:
    """Ensure the standard benchmark suite runs and produces output files."""
    results = asyncio.run(run_standard_benchmarks(tmp_path))
    assert {"coding", "repo_reasoning", "q_and_a"} <= set(results.keys())
    metrics_files = list(tmp_path.glob("*_metrics.json"))
    assert metrics_files, "metrics file not written"

