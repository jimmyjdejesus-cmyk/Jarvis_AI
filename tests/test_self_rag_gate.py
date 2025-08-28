import logging

from jarvis.retrieval.self_rag_gate import SelfRAGGate


def test_should_retrieve_logs_and_records(caplog):
    gate = SelfRAGGate()
    results = [{"relevant": True}, {"relevant": False}]
    with caplog.at_level(logging.INFO):
        decision = gate.should_retrieve("q", results)
    assert isinstance(decision, bool)
    assert len(gate.events) == 1
    assert gate.events[0].precision == 0.5
    assert "retrieval decision" in caplog.text
