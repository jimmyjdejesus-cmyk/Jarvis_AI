"""Indexed transcript storage for scoped RAG queries.

This module provides a lightweight in-memory transcript indexer that
supports positive/negative retrieval. It is designed as a placeholder for
future integration with a persistent vector store.

Usage:
    indexer = TranscriptIndexer()
    indexer.index_run(run_id, markdown)
    hits = indexer.query(task)
    # hits["positive"] and hits["negative"] contain markdown citations
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class TranscriptIndexer:
    """Naive transcript indexer storing markdown by run id."""

    transcripts: Dict[str, str] = field(default_factory=dict)
    positive: Dict[str, List[str]] = field(default_factory=dict)
    negative: Dict[str, List[str]] = field(default_factory=dict)

    def index_run(self, run_id: str, markdown: str) -> None:
        """Store markdown transcript for ``run_id``."""
        self.transcripts[run_id] = markdown

    def add_feedback(self, run_id: str, positive: bool) -> None:
        """Record whether a run should be treated as positive or negative."""
        bucket = self.positive if positive else self.negative
        bucket.setdefault(run_id, []).append(self.transcripts.get(run_id, ""))

    def query(self, task: str) -> Dict[str, List[str]]:
        """Return positive and negative citations related to ``task``.

        The current implementation simply returns all stored transcripts.
        Future revisions will use semantic search to filter results.
        """
        return {
            "positive": [c for runs in self.positive.values() for c in runs],
            "negative": [c for runs in self.negative.values() for c in runs],
        }
