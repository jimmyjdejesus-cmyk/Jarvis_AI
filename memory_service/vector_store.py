"""Vector store configuration using Chroma."""

from __future__ import annotations

from typing import Any, Dict

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
    _store: Dict[str, str] = {}

    def add_text(principal: str, scope: str, key: str, text: str) -> None:
        _store[f"{principal}:{scope}:{key}"] = text

    def query_text(query: str, n_results: int = 5) -> Dict[str, Any]:
        # Naive substring search for compatibility
        matches = [
            text for text in _store.values() if query.lower() in text.lower()
        ][:n_results]
        return {"documents": [matches]}

    def delete_text(principal: str, scope: str, key: str) -> None:
        _store.pop(f"{principal}:{scope}:{key}", None)
