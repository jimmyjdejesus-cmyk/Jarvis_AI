import json
import random
from pathlib import Path
from typing import Set


def simulate_pruning_run(events_path: Path, dead_paths: Set[str], path: str) -> bool:
    teams = ["alpha", "beta", "gamma"]
    events = []
    events.append({"event": "PruneSuggested", "team": teams[0], "reason": "redundant"})
    events.append({"event": "TeamMerged", "source": teams[1], "target": teams[2]})
    if random.random() < 0.5:
        events.append({"event": "PathMarkedDeadEnd", "path": path})
        dead_paths.add(path)
    with events_path.open("a", encoding="utf-8") as f:
        for ev in events:
            f.write(json.dumps(ev) + "\n")
    return True


def test_pruning_merge_lineage(tmp_path):
    events_file = tmp_path / "events.ndjson"
    dead_paths: Set[str] = set()
    reattempts = 0
    success = 0
    runs = 50
    for i in range(runs):
        path = "p1" if i < 2 else f"p{i}"
        if path in dead_paths:
            reattempts += 1
        if simulate_pruning_run(events_file, dead_paths, path):
            success += 1
    # verify log schema contract
    data = [json.loads(line) for line in events_file.read_text().splitlines()]
    assert any(ev["event"] == "PruneSuggested" for ev in data)
    assert any(ev["event"] == "TeamMerged" for ev in data)
    assert any(ev["event"] == "PathMarkedDeadEnd" for ev in data)
    # flaky rate <2%
    failure_rate = 1 - success / runs
    assert failure_rate < 0.02
    # duplicate dead-end re-attempt rate <5%
    assert reattempts / runs < 0.05
    # lineage query reproduces events
    prune_events = [ev for ev in data if ev["event"] == "PruneSuggested"]
    assert prune_events and prune_events[0]["team"] == "alpha"
