"""Lightweight shim for sentence_transformers used in tests.

Provides a minimal `SentenceTransformer` implementation and a `util`
submodule with `cos_sim` so legacy modules can import them during test
collection without installing the real package.
"""

from __future__ import annotations

import numpy as np


class SentenceTransformer:
    def __init__(self, model_name: str = "dummy"):
        self.model_name = model_name

    def encode(self, texts, convert_to_tensor: bool = False):
        # Return deterministic zero embeddings with small dimension.
        n = len(texts) if hasattr(texts, "__len__") else 1
        emb = np.zeros((n, 8), dtype=float)
        if convert_to_tensor:
            return emb
        return emb


# Provide a lightweight util module with cos_sim
class util:  # pragma: no cover - simple shim
    @staticmethod
    def cos_sim(a, b):
        # a, b expected as numpy arrays
        a = np.asarray(a)
        b = np.asarray(b)
        return np.zeros((a.shape[0], b.shape[0]), dtype=float)
