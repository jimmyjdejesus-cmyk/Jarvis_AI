import asyncio
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from benchmarks.harness import BenchmarkScenario, BenchmarkRunner, benchmark_table


def test_benchmark_relevance_and_citations() -> None:
    async def scenario(ctx):
        return {"answer": "response [cite]", "citations": ["doc1"], "relevance": 0.75}

    runner = BenchmarkRunner([BenchmarkScenario("demo", scenario)], concurrency=1)
    results = asyncio.run(runner.run("balanced"))
    metric = results["demo"]
    assert metric.citation_count == 1
    assert metric.answer_relevance == pytest.approx(0.75)
    table = benchmark_table(results, results)
    assert table[0]["citations_balanced"] == 1
    assert table[0]["relevance_balanced"] == pytest.approx(0.75)
