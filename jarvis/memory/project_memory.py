"""Project-level memory storage using Chroma."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

try:
    import chromadb
    from chromadb.utils import embedding_functions
except Exception as e:  # pragma: no cover - runtime import guard
    chromadb = None
    embedding_functions = None  # type: ignore


class MemoryManager:
    """Interface for reading and writing project memory."""

    def add(self, project: str, session: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Store a text snippet in memory."""
        raise NotImplementedError

    def query(self, project: str, session: str, text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Query similar text from memory."""
        raise NotImplementedError


class HashEmbeddingFunction(embedding_functions.EmbeddingFunction if embedding_functions else object):
    """Simple deterministic embedding function.

    This avoids heavy model downloads by hashing text into a single float value.
    """

    def __call__(self, texts: List[str]) -> List[List[float]]:  # type: ignore[override]
        return [[float(abs(hash(t)) % 1024)] for t in texts]


@dataclass
class ProjectMemory(MemoryManager):
    """Chroma-backed vector memory keyed by project and session."""

    persist_directory: str = "data/project_memory"
    _client: Any = None
    _collections: Dict[str, Any] = None

    def __post_init__(self) -> None:
        if chromadb is None:  # pragma: no cover - import guard
            raise ImportError("chromadb is required for ProjectMemory")
        self._client = chromadb.PersistentClient(path=self.persist_directory)
        self._collections = {}
        self._embedding_fn = HashEmbeddingFunction()

    def _key(self, project: str, session: str) -> str:
        return f"{project}_{session}"

    def _get_collection(self, project: str, session: str):
        key = self._key(project, session)
        if key not in self._collections:
            self._collections[key] = self._client.get_or_create_collection(
                name=key,
                embedding_function=self._embedding_fn,
            )
        return self._collections[key]

    # MemoryManager interface -------------------------------------------------
    def add(self, project: str, session: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        collection = self._get_collection(project, session)
        collection.add(ids=[str(uuid.uuid4())], documents=[text], metadatas=[metadata or {}])

    def query(self, project: str, session: str, text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        collection = self._get_collection(project, session)
        results = collection.query(query_texts=[text], n_results=top_k)
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        return [
            {"text": doc, "metadata": meta}
            for doc, meta in zip(docs, metas)
        ]
