"""Lightweight repository knowledge graph.

Maps files to their defined functions for persistent world modeling."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List
import ast


@dataclass
class KnowledgeGraph:
    """Track basic structural relationships in a code repository."""

    files: Dict[str, Dict[str, List[str]]] = field(default_factory=dict)

    def add_file(self, path: str) -> None:
        """Ensure a file node exists."""
        self.files.setdefault(path, {"functions": []})

    def add_function(self, path: str, name: str) -> None:
        """Record a function defined within a file."""
        self.add_file(path)
        functions = self.files[path]["functions"]
        if name not in functions:
            functions.append(name)

    def get_files(self) -> List[str]:
        """Return all tracked file paths."""
        return list(self.files.keys())

    def get_functions(self, path: str) -> List[str]:
        """Return functions known for a given file."""
        return self.files.get(path, {}).get("functions", [])

    def index_repository(self, repo_path: Path, files: List[str]) -> None:
        """Populate the graph with files and function names."""
        for rel in files:
            full_path = Path(repo_path) / rel
            self.add_file(str(full_path))
            if full_path.suffix != ".py":
                continue
            try:
                tree = ast.parse(full_path.read_text(encoding="utf-8"))
            except Exception:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    self.add_function(str(full_path), node.name)