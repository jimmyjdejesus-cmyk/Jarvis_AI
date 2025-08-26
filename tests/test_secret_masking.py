from __future__ import annotations

from memory_service import EVENTS, SENSITIVE_VALUES, _emit


def test_secret_masking_in_events() -> None:
    EVENTS.clear()
    SENSITIVE_VALUES.clear()
    SENSITIVE_VALUES.append("topsecret")
    _emit("read", "topsecret", "scope", "topsecret")
    event = EVENTS[-1]
    assert event["principal"] == "***"
    assert event["key"] == "***"
