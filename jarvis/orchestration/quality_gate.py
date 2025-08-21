"""Built-quality gate implementation.

The :class:`QualityGate` listens for ``finding`` events on the provided
:class:`~jarvis.orchestration.message_bus.MessageBus` instance.  Findings are
simple dictionaries that may contain a ``status`` field (``"pass"`` or
``"fail"``) or a severity level.  When :meth:`evaluate` is invoked all
collected findings are assessed and a final ``quality_gate.pass`` or
``quality_gate.fail`` event is emitted on the bus.
"""
from __future__ import annotations

from typing import Any, Dict, List

from .message_bus import MessageBus


class QualityGate:
    """Aggregate findings and emit a pass/fail outcome."""

    def __init__(self, bus: MessageBus, scope: str = "global") -> None:
        self.bus = bus
        self.scope = scope
        self.findings: List[Dict[str, Any]] = []
        # Subscribe to findings for this gate
        self.bus.subscribe("finding", self._collect_finding)

    async def _collect_finding(self, event: Dict[str, Any]) -> None:
        # Only store findings that match our scope
        if event.get("scope") == self.scope:
            self.findings.append(event["payload"])

    async def evaluate(self) -> bool:
        """Evaluate collected findings and publish a result event."""
        failed = any(
            f.get("status") == "fail" or f.get("severity") in {"error", "high"}
            for f in self.findings
        )
        event_type = "quality_gate.pass" if not failed else "quality_gate.fail"
        await self.bus.publish(event_type, {"findings": self.findings}, scope=self.scope)
        return not failed

    def reset(self) -> None:
        self.findings.clear()
