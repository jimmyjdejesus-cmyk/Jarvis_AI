import importlib
import sys
from pathlib import Path

import pytest

repo_root = Path(__file__).resolve().parent.parent
sys.path.append(str(repo_root / "jarvis" / "orchestration"))

MessageBus = importlib.import_module("message_bus").MessageBus


@pytest.mark.asyncio
async def test_publish_includes_normalized_fields():
    bus = MessageBus()
    await bus.publish(
        "demo.event",
        {"foo": "bar"},
        scope="run1",
        run_id="run1",
        step_id="s1",
        parent_id="root",
        log="hello",
    )
    events = bus.get_scope_events("run1")
    assert events[0]["run_id"] == "run1"
    assert events[0]["step_id"] == "s1"
    assert events[0]["parent_id"] == "root"
    assert events[0]["log"] == "hello"
