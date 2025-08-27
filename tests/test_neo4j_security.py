"""Integration tests for ``Neo4jGraph`` using a live database.

These tests require a running Neo4j instance configured via the
``NEO4J_URI``, ``NEO4J_USER`` and ``NEO4J_PASSWORD`` environment variables.
They are skipped when these credentials are missing.
"""

from __future__ import annotations

import keyring
import pytest
from neo4j.exceptions import ServiceUnavailable

from jarvis.world_model.neo4j_graph import Neo4jGraph


@pytest.mark.integration
def test_round_trip_node_creation() -> None:
    """Ensure a node can be created and queried end-to-end."""

    uri = keyring.get_password("jarvis", "NEO4J_URI")
    user = keyring.get_password("jarvis", "NEO4J_USER")
    password = keyring.get_password("jarvis", "NEO4J_PASSWORD")
    if not uri or not user or not password:
        pytest.skip("Neo4j credentials not configured in keyring")

    graph = Neo4jGraph(uri=uri, user=user, password=password)
    try:
        graph.add_node("integration_test", "Test", {"foo": "bar"})
        with graph.driver.session() as session:
            result = session.run(
                "MATCH (n:Node {id: $id}) RETURN n.foo AS foo",
                id="integration_test",
            )
            assert result.single()["foo"] == "bar"
    finally:
        graph.close()