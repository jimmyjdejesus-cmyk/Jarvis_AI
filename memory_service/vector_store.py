"""Vector store configuration using Chroma."""

from __future__ import annotations

from typing import Any, Dict

from cryptography.fernet import Fernet
from config.secrets import get_secret

try:  # pragma: no cover - optional dependency
    import chromadb
except Exception:  # pragma: no cover - runtime guard
    chromadb = None  # type: ignore


if chromadb:
    _client = chromadb.Client()
    _collection = _client.get_or_create_collection("shared_memory")

    def add_text(principal: str, scope: str, key: str, text: str) -> None:
        """Add a text document to the vector store."""
        _collection.add(
            ids=[f"{principal}:{scope}:{key}"],
            documents=[text],
            metadatas=[{"principal": principal, "scope": scope, "key": key}],
        )

    def query_text(query: str, n_results: int = 5) -> Dict[str, Any]:
        """Query similar text from the store."""
        return _collection.query(query_texts=[query], n_results=n_results)

    def delete_text(principal: str, scope: str, key: str) -> None:
        """Remove a document from the vector store."""
        _collection.delete(ids=[f"{principal}:{scope}:{key}"])

else:  # Fallback minimal implementations for environments without chromadb
    _store: Dict[str, bytes] = {}
    _key = get_secret("MEMORY_ENCRYPTION_KEY")
    if not _key:
        _key = Fernet.generate_key().decode()
    _fernet = Fernet(_key.encode())

    def add_text(principal: str, scope: str, key: str, text: str) -> None:
        token = _fernet.encrypt(text.encode())
        _store[f"{principal}:{scope}:{key}"] = token

    def query_text(query: str, n_results: int = 5) -> Dict[str, Any]:
        # Naive substring search for compatibility
        matches: list[str] = []
        for token in _store.values():
            plaintext = _fernet.decrypt(token).decode()
            if query.lower() in plaintext.lower():
                matches.append(plaintext)
        return {"documents": [matches[:n_results]]}

    def delete_text(principal: str, scope: str, key: str) -> None:
        _store.pop(f"{principal}:{scope}:{key}", None)
