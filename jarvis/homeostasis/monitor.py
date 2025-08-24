"""System resource monitoring service."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

import time

from jarvis.observability.logger import get_logger
from jarvis.learning.root_cause_analyzer import RootCauseAnalyzer
from jarvis.learning.remediation_agent import RemediationAgent

try:  # pragma: no cover - optional dependency
    import psutil
except Exception:  # pragma: no cover
    psutil = None  # type: ignore

@dataclass
class ResourceSnapshot:
    """Current view of system resources."""

    cpu: float
    memory: float
    api_tokens: int


class SystemMonitor:
    """Track system health metrics and detect anomalies."""

    def __init__(
        self,
        cpu_threshold: float = 90.0,
        memory_threshold: float = 90.0,
        analyzer: Optional[RootCauseAnalyzer] = None,
        remediation_agent: Optional[RemediationAgent] = None,
    ) -> None:
        self.api_tokens: int = 0
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.anomaly_start: Optional[float] = None
        self.manual_interventions: int = 0
        self.analyzer = analyzer or RootCauseAnalyzer()
        self.remediation_agent = remediation_agent or RemediationAgent()
        self.logger = get_logger(__name__)

    # ------------------------------------------------------------------
    def record_tokens(self, count: int) -> None:
        """Increment token usage counter."""

        self.api_tokens += max(count, 0)

    # ------------------------------------------------------------------
    def snapshot(self) -> ResourceSnapshot:
        """Return current resource utilization."""

        if psutil:
            cpu = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory().percent
        else:  # pragma: no cover - best effort when psutil missing
            cpu = mem = 0.0
        return ResourceSnapshot(cpu=cpu, memory=mem, api_tokens=self.api_tokens)

    # ------------------------------------------------------------------
    def as_dict(self) -> Dict[str, float]:
        """Convenience wrapper returning metrics as a dict."""

        snap = self.snapshot()
        return {"cpu": snap.cpu, "memory": snap.memory, "api_tokens": snap.api_tokens}

    # ------------------------------------------------------------------
    def _anomaly_detected(self, snap: ResourceSnapshot) -> bool:
        """Return True when resource usage exceeds configured thresholds."""

        return snap.cpu > self.cpu_threshold or snap.memory > self.memory_threshold

    # ------------------------------------------------------------------
    def check_and_remediate(self, trajectory: List[str], dependencies: List[str]) -> bool:
        """Detect anomalies and attempt remediation.

        When resource usage crosses the defined thresholds the method records
        the start time of the incident, performs root cause analysis and invokes
        the remediation agent.  Successful remediation logs the mean time to
        recovery (MTTR) while failed remediation increments the manual
        intervention counter.

        Parameters
        ----------
        trajectory: List[str]
            Recent execution steps leading up to the anomaly.
        dependencies: List[str]
            Components involved in the execution path.

        Returns
        -------
        bool
            ``True`` when the remediation succeeds or no anomaly is detected,
            ``False`` otherwise.
        """

        snap = self.snapshot()
        if not self._anomaly_detected(snap):
            return True

        if self.anomaly_start is None:
            self.anomaly_start = time.monotonic()
            self.logger.warning(
                "anomaly detected",
                extra={"event_type": "anomaly", "data": snap.__dict__},
            )

        root_cause = self.analyzer.analyze(trajectory, dependencies)
        success = self.remediation_agent.remediate(root_cause["component"])

        if success:
            mttr = time.monotonic() - self.anomaly_start if self.anomaly_start else 0.0
            self.logger.info(
                "recovered from anomaly",
                extra={"event_type": "remediation", "data": {"mttr": mttr}},
            )
            self.anomaly_start = None
            return True

        self.manual_interventions += 1
        self.logger.error(
            "manual intervention required",
            extra={
                "event_type": "manual_intervention",
                "data": {"count": self.manual_interventions},
            },
        )
        return False

