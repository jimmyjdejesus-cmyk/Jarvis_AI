import asyncio
import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from benchmarks import BenchmarkScenario, BenchmarkRunner, benchmark_table


async def dummy_scenario(context):
    # Simulate some response; using caching to test functionality
    cached = context.get_cached("prompt")
    if cached:
        return cached
    context.set_cached("prompt", "ok")
    await asyncio.sleep(0)
    return "ok"


def test_runner_collects_metrics():
    runner = BenchmarkRunner([BenchmarkScenario("dummy", dummy_scenario)])
    balanced = asyncio.run(runner.run("balanced"))
    no_prune = asyncio.run(runner.run("no-prune"))
    table = benchmark_table(balanced, no_prune)
    assert table[0]["scenario"] == "dummy"
    assert 0 <= table[0]["token_savings"] <= 1
    assert table[0]["success_balanced"] == 1.0
    assert table[0]["token_cost_no_prune"] >= 0
