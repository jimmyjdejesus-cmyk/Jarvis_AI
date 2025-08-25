import pytest

from jarvis.retrieval.self_rag_gate import SelfRAGGate


def test_gate_allows_when_metrics_good(monkeypatch):
    gate = SelfRAGGate(enabled=True, precision_threshold=0.5, max_latency_ms=200)
    results = [{"relevant": True}, {"relevant": False}]

    timings = iter([0.0, 0.1])  # 100 ms latency
    monkeypatch.setattr("jarvis.retrieval.self_rag_gate.perf_counter", lambda: next(timings))

    assert gate.should_retrieve("query", results) is True
    event = gate.events[-1]
    assert event.precision == pytest.approx(0.5)
    assert event.latency_ms == pytest.approx(100.0)


def test_gate_respects_disable():
    gate = SelfRAGGate(enabled=False)
    assert gate.should_retrieve("q", []) is False
    event = gate.events[-1]
    assert event.precision == 0.0


def test_gate_blocks_on_precision():
    gate = SelfRAGGate(enabled=True, precision_threshold=0.6)
    results = [{"relevant": False}, {"relevant": False}]
    assert gate.should_retrieve("q", results) is False
    assert gate.events[-1].precision == 0.0


def test_gate_blocks_on_latency(monkeypatch):
    gate = SelfRAGGate(enabled=True, precision_threshold=0.0, max_latency_ms=50)

    timings = iter([0.0, 0.2])  # 200 ms latency
    monkeypatch.setattr("jarvis.retrieval.self_rag_gate.perf_counter", lambda: next(timings))

    assert gate.should_retrieve("q", []) is False
    assert gate.events[-1].latency_ms == pytest.approx(200.0)
