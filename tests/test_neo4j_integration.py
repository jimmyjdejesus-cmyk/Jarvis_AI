"""Integration tests for ``Neo4jGraph`` using a live database.

These tests require a running Neo4j instance configured via the
``NEO4J_URI``, ``NEO4J_USER`` and ``NEO4J_PASSWORD`` environment variables.
They are skipped when these credentials are missing.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "jarvis" / "world_model"))
from neo4j_graph import Neo4jGraph

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

pytestmark = pytest.mark.skipif(
    not all([NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD]),
    reason="Neo4j credentials not configured",
)


@pytest.mark.integration
def test_round_trip_node_creation() -> None:
    """Ensure a node can be created and queried end-to-end."""

    graph = Neo4jGraph(uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD)
    try:
        graph.add_node("integration_test", "Test", {"foo": "bar"})
        with graph.driver.session() as session:
            result = session.run(
                "MATCH (n:Node {id: $id}) RETURN n.foo AS foo", id="integration_test"
            )
            assert result.single()["foo"] == "bar"
    finally:
        graph.close()

