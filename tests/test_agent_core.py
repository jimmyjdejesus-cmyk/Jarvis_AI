import pytest

from agent.core import AgentCore


def test_agent_core_components() -> None:
    bus = object()
    memory = object()
    extra = object()

    core = AgentCore(
        config={"a": 1},
        event_bus=bus,
        memory=memory,
        extra=extra,
    )

    assert core.config == {"a": 1}
    assert core.event_bus is bus
    assert core.memory is memory
    assert core.get_component("extra") is extra

    another = object()
    core.add_component("another", another)
    assert core.get_component("another") is another
    assert core.another is another

    with pytest.raises(KeyError):
        core.get_component("missing")
