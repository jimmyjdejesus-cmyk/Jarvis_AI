"""Integration tests for Neo4jGraph using a live database.

These tests require a running Neo4j instance configured via the
``NEO4J_URI``, ``NEO4J_USER`` and ``NEO4J_PASSWORD`` environment variables.
If the database is unavailable the tests are skipped.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from neo4j.exceptions import ServiceUnavailable

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "jarvis" / "world_model"))
from neo4j_graph import Neo4jGraph


@pytest.mark.integration
def test_round_trip_node_creation() -> None:
    """Ensure a node can be created and queried end-to-end."""

    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    if not uri or not user or not password:
        pytest.skip("Neo4j credentials not configured")

    graph = Neo4jGraph(uri=uri, user=user, password=password)
    try:
        graph.add_node("integration_test", "Test", {"foo": "bar"})
        with graph.driver.session() as session:
            result = session.run(
                "MATCH (n:Node {id: $id}) RETURN n.foo AS foo", id="integration_test"
            )
            assert result.single()["foo"] == "bar"
    except ServiceUnavailable:
        pytest.skip("Neo4j service not available")
    finally:
        graph.close()

