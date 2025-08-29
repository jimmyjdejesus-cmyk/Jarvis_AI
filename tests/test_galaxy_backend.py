"""Tests for the Galaxy Model analysis API."""

from fastapi.testclient import TestClient
import numpy as np

from app import galaxy


def test_extract_answer():
    """Answers are extracted from boxed tags."""
    assert galaxy.extract_answer("The result is \\boxed{42}.") == "42"
    assert galaxy.extract_answer("No box here") == ""


def test_calculate_lowest_group_confidence():
    """Confidence uses the lowest unique-token ratio per group."""
    trace = " ".join(["a"] * 5 + ["b"] * 5)
    assert galaxy.calculate_lowest_group_confidence(trace, 5) == 0.2
    assert galaxy.calculate_lowest_group_confidence("", 5) == 0.0


def test_run_galaxy_analysis(monkeypatch):
    """Endpoint returns nodes and similarity links."""

    def fake_generate(prompt: str, k: int):
        return [
            "Thought path one leading to \\boxed{10}.",
            "Alternative reasoning ending with \\boxed{10}.",
        ]

    class DummyModel:
        def encode(self, texts, convert_to_tensor=True):
            return np.array([[1.0, 0.0], [0.0, 1.0]])

    monkeypatch.setattr(
        galaxy.llm_generator, "generate_k_traces", fake_generate
    )
    monkeypatch.setattr(galaxy, "get_similarity_model", lambda: DummyModel())
    monkeypatch.setattr(
        galaxy.util,
        "cos_sim",
        lambda a, b: np.array([[1.0, 0.8], [0.8, 1.0]]),
    )

    client = TestClient(galaxy.app)
    resp = client.post("/analyze", json={"prompt": "test"})
    assert resp.status_code == 200
    data = resp.json()["graph_data"]
    assert len(data["nodes"]) == 2
    assert data["nodes"][0]["answer"] == "10"
    assert data["links"][0]["strength"] == 0.8
