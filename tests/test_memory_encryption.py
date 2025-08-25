"""Tests for encryption at rest in the vector store fallback."""
import importlib
from cryptography.fernet import Fernet


def test_vector_store_encrypts_at_rest(monkeypatch):
    key = Fernet.generate_key()
    monkeypatch.setenv("MEMORY_ENCRYPTION_KEY", key.decode())
    vs = importlib.reload(importlib.import_module("memory_service.vector_store"))
    vs.add_text("u", "s", "k", "secret data")
    raw = vs._store["u:s:k"]
    assert b"secret data" not in raw
    result = vs.query_text("secret data")
    assert "secret data" in result["documents"][0][0]
