import asyncio

from jarvis.orchestration import HierarchicalMessageBus


def test_hierarchical_routing():
    bus = HierarchicalMessageBus()
    received = []

    def handler_factory(name):
        def handler(message):
            received.append((name, message["type"]))
        return handler

    bus.subscribe("team", handler_factory("team"))
    bus.subscribe("team.dev", handler_factory("team.dev"))
    bus.subscribe("*", handler_factory("all"))

    asyncio.run(bus.publish("team.dev.coder", {"data": 1}, scope="s1"))

    assert ("team", "team.dev.coder") in received
    assert ("team.dev", "team.dev.coder") in received
    assert ("all", "team.dev.coder") in received
