"""Project-level memory storage using Chroma."""

from __future__ import annotations

import uuid
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

try:
    import chromadb
    from chromadb.utils import embedding_functions
except ImportError as e:  # pragma: no cover - runtime import guard
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
        import hashlib
        DIM = 8  # Number of dimensions for the embedding
        def hash_to_vec(text: str) -> List[float]:
            # Use sha256 to get a deterministic 32-byte hash
            h = hashlib.sha256(text.encode("utf-8")).digest()
            # Split into DIM chunks and convert each to a float
            return [
                float(int.from_bytes(h[i*4:(i+1)*4], "big") % 1024)
                for i in range(DIM)
            ]
        return [hash_to_vec(t) for t in texts]


@dataclass
class ProjectMemory(MemoryManager):
    """Chroma-backed vector memory keyed by project and session."""

    persist_directory: str = "data/project_memory"
    _client: Optional[Any] = None
    _collections: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if chromadb is None:  # pragma: no cover - import guard
            raise ImportError("chromadb is required for ProjectMemory")
        os.makedirs(self.persist_directory, exist_ok=True)
        self._client = chromadb.PersistentClient(path=self.persist_directory)
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
