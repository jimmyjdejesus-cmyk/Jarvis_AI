from pathlib import Path
from unittest.mock import MagicMock, patch

import keyring
import pytest
import os
from fastapi.testclient import TestClient
from app.main import app
from jarvis.security.secret_manager import get_secret, set_secret

from jarvis.world_model.neo4j_graph import Neo4jGraph


def test_credentials_loaded_from_keyring():
    keyring.set_password("jarvis", "NEO4J_URI", "bolt://neo4j.test")
    keyring.set_password("jarvis", "NEO4J_USER", "user")
    keyring.set_password("jarvis", "NEO4J_PASSWORD", "secret")

    # Patch target updated to match the new direct import path
    with patch("jarvis.world_model.neo4j_graph.GraphDatabase.driver") as mock_driver:
        Neo4jGraph()
        mock_driver.assert_called_once_with(
            "bolt://neo4j.test", auth=("user", "secret")
        )


def test_add_edge_rejects_invalid_relationship():
    graph = Neo4jGraph(driver=MagicMock())
    with pytest.raises(ValueError):
        graph.add_edge("a", "b", "end-1")


def test_add_edge_runs_with_valid_relationship():
    driver = MagicMock()
    graph = Neo4jGraph(driver=driver)
    graph.add_edge("a", "b", "knows")
    driver.session.return_value.__enter__.return_value.run.assert_called_once()


def test_set_secret_round_trip():
    set_secret("API_TEST", "123")
    assert get_secret("API_TEST") == "123"


def test_update_credentials_endpoint():
    os.environ["JARVIS_API_KEY"] = "test-key"
    client = TestClient(app)
    payload = {
        "uri": "bolt://api.test",
        "user": "neo",
        "password": "matrix",
    }
    r = client.post(
        "/settings/neo4j",
        json=payload,
        headers={"X-API-Key": "test-key"},
    )
    assert r.status_code == 200
    assert get_secret("NEO4J_URI") == "bolt://api.test"
    assert get_secret("NEO4J_USER") == "neo"
    assert get_secret("NEO4J_PASSWORD") == "matrix"