import asyncio
import sys
from pathlib import Path

# Ensure repository root on path for direct test invocation
sys.path.append(str(Path(__file__).resolve().parents[1]))

from benchmarks.harness import run_standard_benchmarks  # noqa: E402


def test_run_standard_benchmarks(tmp_path: Path) -> None:
    results = asyncio.run(run_standard_benchmarks(tmp_path))
    assert {"coding", "repo_reasoning", "q_and_a"} <= set(results.keys())
    metrics_files = list(tmp_path.glob("*_metrics.json"))
    assert metrics_files, "metrics file not written"
