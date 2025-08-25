"""Simple performance gate for CI.

Given two JSON files containing benchmark metrics, this script fails with a
non-zero exit code if any metric regresses more than the allowed percentage.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def load_metrics(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)


def main() -> int:
    if len(sys.argv) != 4:
        part1 = "usage: perf_gate.py <baseline.json>"
        part2 = "<candidate.json> <max_regression>"
        usage = f"{part1} {part2}"
        print(usage)
        return 1
    baseline = load_metrics(Path(sys.argv[1]))
    candidate = load_metrics(Path(sys.argv[2]))
    limit = float(sys.argv[3])

    for name, base in baseline.items():
        cand = candidate.get(name, {})
        for metric in ("total_latency", "token_count", "token_cost"):
            b = base.get(metric, 0.0)
            c = cand.get(metric, 0.0)
            if b and c and (c - b) / b > limit:
                print(f"Regression in {name}:{metric} -> {b} vs {c}")
                return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
