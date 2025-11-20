from __future__ import annotations

import statistics
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Deque, Dict, Iterable, List, Optional


@dataclass
class MetricSnapshot:
    request_count: int
    average_latency_ms: float
    max_latency_ms: float
    tokens_generated: int
    context_tokens: int
    personas_used: Dict[str, int]
    timestamp: float = field(default_factory=time.time)


class MetricsRegistry:
    """In-memory metrics registry with rolling history for harvesting."""

    def __init__(self, history_size: int = 120):
        self._lock = threading.RLock()
        self._latencies: List[float] = []
        self._tokens_generated: int = 0
        self._context_tokens: int = 0
        self._personas_used: Dict[str, int] = defaultdict(int)
        self._request_count: int = 0
        self._history: Deque[MetricSnapshot] = deque(maxlen=history_size)

    def record_request(self, persona: str, latency_ms: float, generated_tokens: int, context_tokens: int) -> None:
        with self._lock:
            self._request_count += 1
            self._latencies.append(latency_ms)
            self._tokens_generated += generated_tokens
            self._context_tokens += context_tokens
            self._personas_used[persona] += 1

    def harvest(self) -> MetricSnapshot:
        with self._lock:
            if self._latencies:
                avg_latency = statistics.mean(self._latencies)
                max_latency = max(self._latencies)
            else:
                avg_latency = 0.0
                max_latency = 0.0
            snapshot = MetricSnapshot(
                request_count=self._request_count,
                average_latency_ms=avg_latency,
                max_latency_ms=max_latency,
                tokens_generated=self._tokens_generated,
                context_tokens=self._context_tokens,
                personas_used=dict(self._personas_used),
            )
            self._history.append(snapshot)
            self._latencies.clear()
            self._tokens_generated = 0
            self._context_tokens = 0
            self._personas_used.clear()
            self._request_count = 0
            return snapshot

    def history(self) -> Iterable[MetricSnapshot]:
        with self._lock:
            return list(self._history)


@dataclass
class TraceRecord:
    trace_id: str
    span_id: str
    persona: str
    objective: str
    latency_ms: float
    token_usage: int
    context_size: int
    timestamp: float = field(default_factory=time.time)
    backend: Optional[str] = None
    extra: Dict[str, str] = field(default_factory=dict)


class TraceCollector:
    """Collects trace records for auditing and performance analysis."""

    def __init__(self, max_records: int = 5000):
        self._lock = threading.RLock()
        self._records: Deque[TraceRecord] = deque(maxlen=max_records)

    def add(self, record: TraceRecord) -> None:
        with self._lock:
            self._records.append(record)

    def latest(self, limit: int = 50) -> List[TraceRecord]:
        with self._lock:
            return list(self._records)[-limit:]

    def filter_by_persona(self, persona: str, limit: int = 50) -> List[TraceRecord]:
        with self._lock:
            return [record for record in reversed(self._records) if record.persona == persona][:limit]


__all__ = [
    "MetricsRegistry",
    "MetricSnapshot",
    "TraceCollector",
    "TraceRecord",
]
