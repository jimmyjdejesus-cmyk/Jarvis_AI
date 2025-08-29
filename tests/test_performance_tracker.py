from jarvis.monitoring.performance import PerformanceTracker


def test_retry_counts_for_success_and_failure():
    tracker = PerformanceTracker()

    tracker.record_event("step", success=False, attempt=1)
    assert tracker.metrics["failed_steps"] == 1
    assert tracker.metrics["retry_attempts"] == 0

    tracker.record_event("step", success=True, attempt=2)
    assert tracker.metrics["retry_attempts"] == 1
    assert tracker.metrics["failed_steps"] == 1

    tracker.record_event("step", success=False, attempt=3)
    assert tracker.metrics["retry_attempts"] == 2
    assert tracker.metrics["failed_steps"] == 2


def test_retry_counts_increment_only_for_attempts_beyond_first():
    tracker = PerformanceTracker()

    tracker.record_event("step", success=True, attempt=1)
    tracker.record_event("step", success=True, attempt=1)
    assert tracker.metrics["retry_attempts"] == 0

    tracker.record_event("step", success=True, attempt=2)
    tracker.record_event("step", success=True, attempt=5)
    assert tracker.metrics["retry_attempts"] == 2
