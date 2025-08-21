import json
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Any
import zlib

import numpy as np

try:
    import faiss  # type: ignore
except Exception:  # pragma: no cover - handled at runtime
    faiss = None


class RepositoryIndexer:
    """Simple repository indexer using hashed embeddings and FAISS."""

    def __init__(self, repo_path: Path | str = Path.cwd(), index_dir: Path | str = Path("data/repo_index"), dim: int = 300):
        self.repo_path = Path(repo_path)
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.dim = dim
        self.version = self._get_repo_version()
        self.index_file = self.index_dir / f"index_{self.version}.faiss"
        self.embeddings_file = self.index_dir / f"index_{self.version}.npy"
        self.meta_file = self.index_dir / f"index_{self.version}.json"
        self.index: Optional[Any] = None
        self.embeddings: Optional[np.ndarray] = None
        self.files: List[str] = []
        self.snippets: List[str] = []
        self._load_index()

    def _get_repo_version(self) -> str:
        """Get current repository commit hash for versioning."""
        try:
            return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.repo_path).decode().strip()
        except Exception:
            return "unknown"

    def _load_index(self) -> None:
        """Load existing index and cached snippets if available."""
        if self.meta_file.exists():
            meta = json.loads(self.meta_file.read_text())
            self.files = meta.get("files", [])
            self.snippets = meta.get("snippets", [])

        if faiss and self.index_file.exists():
            self.index = faiss.read_index(str(self.index_file))
        elif self.embeddings_file.exists():
            try:
                self.embeddings = np.load(self.embeddings_file)
            except Exception:
                self.embeddings = None

    def _embed(self, text: str) -> np.ndarray:
        """Create a simple deterministic hashed embedding for text."""
        vec = np.zeros(self.dim, dtype="float32")
        for token in text.split():
            idx = zlib.crc32(token.encode()) % self.dim
            vec[idx] += 1.0
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec

    def _iter_files(self) -> List[Path]:
        """Yield repository files to index."""
        exts = {".py", ".md", ".txt", ".rst", ".json", ".yaml", ".yml"}
        return [p for p in self.repo_path.rglob("*") if p.is_file() and p.suffix in exts]

    def build_index(self, force_rebuild: bool = False) -> None:
        """Build or rebuild the repository index and cache file snippets."""
        if (self.index is not None or self.embeddings is not None) and not force_rebuild:
            return

        files = self._iter_files()
        if not files:
            return

        embeddings = []
        self.files = []
        self.snippets = []
        for p in files:
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            embeddings.append(self._embed(text))
            self.files.append(str(p.relative_to(self.repo_path)))
            snippet = text[:200].replace("\n", " ")
            self.snippets.append(snippet)

        vectors = np.vstack(embeddings)
        if faiss:
            self.index = faiss.IndexFlatIP(self.dim)
            self.index.add(vectors)
            faiss.write_index(self.index, str(self.index_file))
        else:
            self.embeddings = vectors
            np.save(self.embeddings_file, vectors)

        self.meta_file.write_text(json.dumps({
            "files": self.files,
            "snippets": self.snippets,
            "version": self.version
        }, indent=2))

    def search(self, query: str, k: int = 5) -> List[Dict[str, str]]:
        """Search the repository for relevant files using cached snippets."""
        if self.index is None and self.embeddings is None:
            self.build_index()
        if faiss and self.index is not None:
            q_vec = self._embed(query)
            D, I = self.index.search(np.expand_dims(q_vec, 0), k)
            indices = I[0]
            scores = D[0]
        elif self.embeddings is not None:
            q_vec = self._embed(query)
            scores = self.embeddings @ q_vec
            indices = np.argsort(scores)[::-1][:k]
        else:
            return []

        results = []
        top_scores = scores[indices] if not (faiss and self.index is not None) else scores
        score_iter = scores if (faiss and self.index is not None) else top_scores
        for idx, score in zip(indices, score_iter):
            if idx < 0 or idx >= len(self.files):
                continue
            snippet = self.snippets[int(idx)] if hasattr(self, "snippets") and int(idx) < len(self.snippets) else ""
            results.append({"path": self.files[int(idx)], "score": float(score), "snippet": snippet})
        return results
