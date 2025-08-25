import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from jarvis.homeostasis.monitor import SystemMonitor, ResourceSnapshot
from jarvis.learning.remediation_agent import RemediationAgent
from jarvis.observability.logger import set_correlation_id, load_events


class DummyMonitor(SystemMonitor):
    def snapshot(self) -> ResourceSnapshot:  # type: ignore[override]
        return ResourceSnapshot(cpu=95, memory=95, api_tokens=0)


def test_monitor_records_mttr(tmp_path):
    cid = set_correlation_id()
    actions = {"db": lambda: None}
    monitor = DummyMonitor(remediation_agent=RemediationAgent(actions), cpu_threshold=10, memory_threshold=10)
    ok = monitor.check_and_remediate(["step db"], ["db"])
    events = list(load_events(cid))
    remediation = [e for e in events if e.get("event_type") == "remediation"]
    assert ok is True
    assert remediation and "mttr" in remediation[0]["data"]
    assert monitor.manual_interventions == 0


def test_monitor_logs_manual_intervention(tmp_path):
    cid = set_correlation_id()
    monitor = DummyMonitor(remediation_agent=RemediationAgent({}), cpu_threshold=10, memory_threshold=10)
    ok = monitor.check_and_remediate(["step cache"], ["cache"])
    events = list(load_events(cid))
    assert ok is False
    assert monitor.manual_interventions == 1
    assert any(e.get("event_type") == "manual_intervention" for e in events)


def test_root_cause_analyzer_prefers_frequent_failures():
    from jarvis.learning.root_cause_analyzer import RootCauseAnalyzer

    analyzer = RootCauseAnalyzer()
    traj = ["A fails", "B works", "A again"]
    deps = ["A", "B"]
    first = analyzer.analyze(traj, deps)
    second = analyzer.analyze(traj, deps)
    assert first["component"] == "A"
    assert second["component"] == "A"
