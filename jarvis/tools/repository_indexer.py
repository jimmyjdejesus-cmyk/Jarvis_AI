import json
import subprocess
from pathlib import Path
from typing import List, Dict, Optional

import numpy as np

try:
    import faiss  # type: ignore
except Exception:  # pragma: no cover - handled at runtime
    faiss = None


class RepositoryIndexer:
    """Simple repository indexer using hashed embeddings and FAISS."""

    def __init__(self, repo_path: Path | str = Path.cwd(), index_dir: Path | str = Path("data/repo_index"), dim: int = 300):
        self.repo_path = Path(repo_path)
    def __init__(self, repo_path: Path | str = Path.cwd(), index_dir: Optional[Path | str] = None, dim: int = 300):
        self.repo_path = Path(repo_path)
        # Determine index_dir: environment variable > argument > default relative to repo_path
        env_index_dir = os.environ.get("REPO_INDEX_DIR")
        if index_dir is not None:
            self.index_dir = Path(index_dir)
        elif env_index_dir:
            self.index_dir = Path(env_index_dir)
        else:
            self.index_dir = self.repo_path / "data" / "repo_index"
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.dim = dim
        self.version = self._get_repo_version()
        self.index_file = self.index_dir / f"index_{self.version}.faiss"
        self.meta_file = self.index_dir / f"index_{self.version}.json"
        self.index: Optional[faiss.Index] = None if faiss else None
        self.files: List[str] = []
        if faiss:
            self._load_index()

    def _get_repo_version(self) -> str:
        """Get current repository commit hash for versioning."""
        try:
            return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.repo_path).decode().strip()
        except Exception:
            return "unknown"

    def _load_index(self) -> None:
        """Load existing index if available."""
        if self.index_file.exists() and self.meta_file.exists():
            self.index = faiss.read_index(str(self.index_file))
            meta = json.loads(self.meta_file.read_text())
            self.files = meta.get("files", [])

    def _embed(self, text: str) -> np.ndarray:
        """Create a simple hashed embedding for text."""
        vec = np.zeros(self.dim, dtype="float32")
        for token in text.split():
            idx = hash(token) % self.dim
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
        """Build or rebuild the repository index."""
        if not faiss:
            raise RuntimeError("faiss library is required for indexing")
        if self.index and not force_rebuild:
            return

        files = self._iter_files()
        if not files:
            return

        embeddings = []
        self.files = []
        for p in files:
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            embeddings.append(self._embed(text))
            self.files.append(str(p.relative_to(self.repo_path)))

        vectors = np.vstack(embeddings)
        self.index = faiss.IndexFlatIP(self.dim)
        self.index.add(vectors)
        faiss.write_index(self.index, str(self.index_file))
        self.meta_file.write_text(json.dumps({"files": self.files, "version": self.version}, indent=2))

    def search(self, query: str, k: int = 5) -> List[Dict[str, str]]:
        """Search the repository for relevant files."""
        if not faiss:
            raise RuntimeError("faiss library is required for searching")
        if self.index is None:
            self.build_index()
        if self.index is None:
            return []

        q_vec = self._embed(query)
        D, I = self.index.search(np.expand_dims(q_vec, 0), k)
        results = []
        for score, idx in zip(D[0], I[0]):
            if idx < 0 or idx >= len(self.files):
                continue
            path = self.repo_path / self.files[idx]
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except (FileNotFoundError, PermissionError, UnicodeDecodeError):
                snippet = ""
            else:
                snippet = text[:200].replace("\n", " ")
            results.append({"path": self.files[idx], "score": float(score), "snippet": snippet})
        return results
