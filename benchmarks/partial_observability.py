"""Benchmark utilities for assessing bandwidth penalties under partial observability."""
from __future__ import annotations

from time import perf_counter
from typing import Iterable, Mapping
import sys

try:
    from jarvis.orchestration.bandwidth_channel import BandwidthLimitedChannel
    from jarvis.orchestration.message_bus import MessageBus
except Exception:  # pragma: no cover - allow running without full package
    import importlib
    from pathlib import Path

    module_dir = Path(__file__).resolve().parent.parent / "jarvis" / "orchestration"
    sys_path_added = str(module_dir)
    if sys_path_added not in sys.path:
        sys.path.append(sys_path_added)
    BandwidthLimitedChannel = importlib.import_module("bandwidth_channel").BandwidthLimitedChannel
    MessageBus = importlib.import_module("message_bus").MessageBus


async def benchmark_partial_observability(
    messages: Iterable[Mapping[str, object]],
    visible_fraction: float,
    bandwidth: int = 1024,
) -> float:
    """Benchmark publishing messages with limited visibility.

    Each message is truncated to the given ``visible_fraction`` before being
    published through a bandwidth‑limited channel.  The function returns the
    total time taken to publish all messages.

    Parameters
    ----------
    messages:
        Iterable of payload dictionaries.
    visible_fraction:
        Fraction of keys from each payload that are observable to the receiving
        agents.  The remainder of the message is discarded, modelling partial
        observability.
    bandwidth:
        Channel bandwidth in bytes per second.
    """
    channel = BandwidthLimitedChannel(bandwidth)
    bus = MessageBus(channel=channel)

    start = perf_counter()
    for payload in messages:
        keys = list(payload.keys())
        cutoff = max(1, int(len(keys) * visible_fraction))
        visible = {k: payload[k] for k in keys[:cutoff]}
        await bus.publish("bench.partial", visible)
    return perf_counter() - start
