"""Utilities for indexing a repository into search and graph structures."""

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import zlib

import networkx as nx
import numpy as np

from jarvis.models.client import model_client
from jarvis.world_model.knowledge_graph import KnowledgeGraph

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
        self.chunk_info: List[Dict[str, str]] = []
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
            self.chunk_info = meta.get("chunk_info", [])

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

    def _agentic_chunker(self, file_path: str, text: str) -> List[Dict[str, str]]:
        """Splits text into semantic chunks using an LLM."""
        prompt = f'''
Analyze the following file content from '{file_path}'. Your task is to split the text into semantically coherent chunks. Each chunk should represent a distinct concept, function, class, or section.

Respond with ONLY a valid JSON array of objects. Each object must have two keys: "title" and "content".
- "title": A short, descriptive title for the chunk (e.g., "Function: calculate_area", "Class: UserProfile").
- "content": The actual text content of the chunk.

Here is the file content:
---
{text}
---
'''
        try:
            response_str = model_client.generate_response(model="llama3.2", prompt=prompt)
            if "```json" in response_str:
                response_str = response_str.split("```json")[1].split("```")[0].strip()

            chunks = json.loads(response_str)
            if not isinstance(chunks, list) or not all(isinstance(c, dict) and "title" in c and "content" in c for c in chunks):
                raise ValueError("Invalid chunk structure")
            return chunks
        except (json.JSONDecodeError, ValueError) as e:
            # Fallback for failed chunking
            return [{"title": Path(file_path).name, "content": text}]

    def _iter_files(self) -> List[Path]:
        """Yield repository files to index."""
        exts = {".py", ".md", ".txt", ".rst", ".json", ".yaml", ".yml"}
        return [p for p in self.repo_path.rglob("*") if p.is_file() and p.suffix in exts]

    def build_index(self, force_rebuild: bool = False) -> None:
        """Build or rebuild the repository index using agentic chunking."""
        if (self.index is not None or self.embeddings is not None) and not force_rebuild:
            return

        files = self._iter_files()
        if not files:
            return

        embeddings = []
        self.chunk_info = []
        for p in files:
            file_path_str = str(p.relative_to(self.repo_path))
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            chunks = self._agentic_chunker(file_path_str, text)
            for chunk in chunks:
                embeddings.append(self._embed(chunk["content"]))
                self.chunk_info.append({
                    "path": file_path_str,
                    "title": chunk["title"],
                    "content": chunk["content"]
                })

        if not embeddings:
            return

        vectors = np.vstack(embeddings)
        if faiss:
            self.index = faiss.IndexFlatIP(self.dim)
            self.index.add(vectors)
            faiss.write_index(self.index, str(self.index_file))
        else:
            self.embeddings = vectors
            np.save(self.embeddings_file, vectors)

        self.meta_file.write_text(json.dumps({
            "chunk_info": self.chunk_info,
            "version": self.version
        }, indent=2))

    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search the repository for relevant chunks."""
        if (self.index is None and self.embeddings is None) or not hasattr(self, 'chunk_info') or not self.chunk_info:
            self.build_index()

        if (self.index is None and self.embeddings is None) or not hasattr(self, 'chunk_info') or not self.chunk_info:
            return []

        q_vec = self._embed(query)

        if faiss and self.index is not None:
            scores, indices = self.index.search(np.expand_dims(q_vec, 0), k)
            scores, indices = scores[0], indices[0]
        elif self.embeddings is not None:
            sims = self.embeddings @ q_vec
            indices = np.argsort(sims)[::-1][:k]
            scores = sims[indices]
        else:
            return []

        results = []
        for idx, score in zip(indices, scores):
            idx = int(idx)
            if idx < 0 or idx >= len(self.chunk_info):
                continue

            chunk = self.chunk_info[idx]
            results.append({
                "path": chunk["path"],
                "title": chunk["title"],
                "content": chunk["content"],
                "score": float(score)
            })
        return results

    def _build_cfg(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> List[Tuple[int, int]]:
        """Generate a rudimentary control-flow graph as line-number pairs."""
        edges: List[Tuple[int, int]] = []
        prev_line: Optional[int] = None
        for stmt in node.body:
            line = getattr(stmt, "lineno", None)
            if line is None:
                continue
            if prev_line is not None:
                edges.append((prev_line, line))
            prev_line = line

            if isinstance(stmt, ast.If):
                if stmt.body:
                    edges.append((line, stmt.body[0].lineno))
                if stmt.orelse:
                    edges.append((line, stmt.orelse[0].lineno))
            elif isinstance(stmt, (ast.For, ast.While)):
                if stmt.body:
                    edges.append((line, stmt.body[0].lineno))
                    last = getattr(stmt.body[-1], "lineno", None)
                    if last is not None:
                        edges.append((last, line))
                if stmt.orelse:
                    edges.append((line, stmt.orelse[0].lineno))
        return edges

    def _build_dfg(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> List[Tuple[int, int, str]]:
        """Generate a simple data-flow graph as (def_line, use_line, variable)."""
        class _Visitor(ast.NodeVisitor):
            def __init__(self) -> None:
                self.last_def: Dict[str, int] = {}
                self.edges: List[Tuple[int, int, str]] = []

            def visit_Assign(self, assign: ast.Assign) -> None:
                lineno = assign.lineno
                self.visit(assign.value)
                for target in assign.targets:
                    if isinstance(target, ast.Name):
                        self.last_def[target.id] = lineno
                self.generic_visit(assign)

            def visit_AugAssign(self, assign: ast.AugAssign) -> None:
                self.visit(assign.value)
                if isinstance(assign.target, ast.Name):
                    def_line = self.last_def.get(assign.target.id)
                    if def_line is not None:
                        self.edges.append((def_line, assign.lineno, assign.target.id))
                    self.last_def[assign.target.id] = assign.lineno
                self.generic_visit(assign)

            def visit_Name(self, name: ast.Name) -> None:
                if isinstance(name.ctx, ast.Load):
                    def_line = self.last_def.get(name.id)
                    if def_line is not None:
                        self.edges.append((def_line, name.lineno, name.id))
                self.generic_visit(name)

        visitor = _Visitor()
        visitor.visit(node)
        return visitor.edges

    def index_repository(self, graph: Any) -> None:
        """Populate ``graph`` with code entities and flow information."""
        for file_path in self.repo_path.rglob("*.py"):
            rel = str(file_path.relative_to(self.repo_path))
            graph.add_node(rel, "file", {"path": rel})
            try:
                tree = ast.parse(file_path.read_text(encoding="utf-8"))
            except Exception:
                continue
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func_id = f"{rel}::{node.name}"
                    cfg = self._build_cfg(node)
                    dfg = self._build_dfg(node)
                    graph.add_node(
                        func_id,
                        "function",
                        {
                            "name": node.name,
                            "file": rel,
                            "ast": ast.dump(node),
                            "cfg": cfg,
                            "dfg": dfg,
                        },
                    )
                    graph.add_edge(rel, func_id, "contains")
                    calls = [
                        n
                        for n in ast.walk(node)
                        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                    ]
                    for call in calls:
                        target = f"{rel}::{call.func.id}"
                        graph.add_node(target, "function")
                        graph.add_edge(func_id, target, "calls")
                elif isinstance(node, ast.ClassDef):
                    class_id = f"{rel}::{node.name}"
                    graph.add_node(class_id, "class", {"name": node.name, "file": rel})
                    graph.add_edge(rel, class_id, "contains")
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        module = alias.name
                        graph.add_node(module, "module")
                        graph.add_edge(rel, module, "imports")
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        target = f"{module}.{alias.name}" if module else alias.name
                        graph.add_node(target, "module")
                        graph.add_edge(rel, target, "imports")

        graph_file = self.index_dir / f"graph_{self.version}.json"
        data = nx.node_link_data(graph.graph)
        graph_file.write_text(json.dumps(data, indent=2))
