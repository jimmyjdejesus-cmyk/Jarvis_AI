import json
import time

import pytest
import importlib
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
sys.path.append(str(repo_root))
module_dir = repo_root / "jarvis" / "orchestration"
sys.path.append(str(module_dir))

BandwidthLimitedChannel = importlib.import_module("bandwidth_channel").BandwidthLimitedChannel
MessageBus = importlib.import_module("message_bus").MessageBus

from benchmarks.partial_observability import benchmark_partial_observability


@pytest.mark.asyncio
async def test_bandwidth_penalty_imposes_delay():
    payload = {"data": "x" * 100}
    channel = BandwidthLimitedChannel(bandwidth=1000)
    bus = MessageBus(channel=channel)

    start = time.perf_counter()
    await bus.publish("demo", payload)
    elapsed = time.perf_counter() - start

    expected_min = len(json.dumps(payload)) / 1000
    assert elapsed >= expected_min
    assert elapsed == pytest.approx(channel.total_penalty, rel=0.1)


@pytest.mark.asyncio
async def test_partial_observability_benchmark_runs():
    messages = [{"a": i, "b": i * 2, "c": i * 3} for i in range(5)]
    runtime = await benchmark_partial_observability(messages, visible_fraction=0.5)
    assert runtime > 0
