"""Tests for Redis-backed Hypergraph storage."""

import fakeredis

from memory_service.hypergraph import Hypergraph
from memory_service.models import Node


def test_add_and_get_node() -> None:
    client = fakeredis.FakeRedis(decode_responses=True)
    hg = Hypergraph(redis_client=client)
    node_id = hg.add_node(Node(node_type="test"))
    fetched = hg.get_node(node_id)
    assert fetched is not None
    assert fetched.node_type == "test"
