"""System resource monitoring service."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import psutil


@dataclass
class ResourceSnapshot:
    """Current view of system resources."""

    cpu: float
    memory: float
    api_tokens: int


class SystemMonitor:
    """Track system health metrics and API token usage."""

    def __init__(self) -> None:
        self.api_tokens: int = 0

    # ------------------------------------------------------------------
    def record_tokens(self, count: int) -> None:
        """Increment token usage counter."""

        self.api_tokens += max(count, 0)

    # ------------------------------------------------------------------
    def snapshot(self) -> ResourceSnapshot:
        """Return current resource utilization."""

        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory().percent
        return ResourceSnapshot(cpu=cpu, memory=mem, api_tokens=self.api_tokens)

    # ------------------------------------------------------------------
    def as_dict(self) -> Dict[str, float]:
        """Convenience wrapper returning metrics as a dict."""

        snap = self.snapshot()
        return {"cpu": snap.cpu, "memory": snap.memory, "api_tokens": snap.api_tokens}

