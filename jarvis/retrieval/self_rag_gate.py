"""Self-RAG gating logic with decision metrics.

The gate analyses retrieval results to determine whether an additional
retrieval step should be performed. Decisions are guided by precision and
latency thresholds. Each evaluation is logged via :class:`RetrievalMetrics`
for later inspection. Future GraphRAG and REX-RAG components will feed their
vector, neighbourhood and code-aware retrieval scores into this gate to keep
the decision pipeline consistent.
"""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import List, Sequence, Dict, Any
import logging


@dataclass
class RetrievalMetrics:
    """Metrics captured for a single retrieval evaluation."""

    precision: float
    latency_ms: float
    decision: bool


class SelfRAGGate:
    """Gate that decides on retrieval triggers for self-RAG workflows.

    Parameters
    ----------
    enabled:
        Whether the gate is active. If ``False`` the gate always blocks
        retrieval.
    precision_threshold:
        Minimum precision required to allow retrieval.
    max_latency_ms:
        Maximum latency in milliseconds tolerated for the gating
        computation.
    """

    def __init__(
        self,
        enabled: bool = True,
        precision_threshold: float = 0.5,
        max_latency_ms: float = 500.0,
    ) -> None:
        self.enabled = enabled
        self.precision_threshold = precision_threshold
        self.max_latency_ms = max_latency_ms
        self.events: List[RetrievalMetrics] = []
        self._logger = logging.getLogger(__name__)

    def _compute_precision(self, results: Sequence[Dict[str, Any]]) -> float:
        """Compute precision for retrieval results.

        Each result may include a boolean ``relevant`` flag indicating
        whether the item is relevant. Precision is the fraction of results
        marked as relevant.
        """

        if not results:
            return 0.0
        relevant = sum(1 for r in results if r.get("relevant"))
        return relevant / len(results)

    def should_retrieve(
        self, query: str, results: Sequence[Dict[str, Any]]
    ) -> bool:
        """Determine whether retrieval should be triggered.

        Parameters
        ----------
        query:
            The query text. Currently unused but reserved for heuristic
            triggers based on query characteristics.
        results:
            Retrieval results containing optional ``relevant`` flags.

        Returns
        -------
        bool
            ``True`` if retrieval should proceed, otherwise ``False``.
        """

        start = perf_counter()
        precision = self._compute_precision(results)
        latency_ms = (perf_counter() - start) * 1000.0

        decision = True
        if not self.enabled:
            decision = False
        elif precision < self.precision_threshold:
            decision = False
        elif latency_ms > self.max_latency_ms:
            decision = False

        metrics = RetrievalMetrics(precision, latency_ms, decision)
        self.events.append(metrics)
        self._logger.info(
            "retrieval decision",
            extra={
                "precision": precision,
                "latency_ms": latency_ms,
                "decision": decision,
            },
        )
        return decision
