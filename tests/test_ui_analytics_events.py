"""Tests for the analytics dashboard utilities."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ui.analytics import build_collaboration_graph, load_event_data


def _write_events(path: Path) -> None:
    events = [
        {"event": "PruneSuggested", "team_id": "team_alpha", "reason": "redundant"},
        {"event": "TeamMerged", "source": "team_beta", "target": "team_gamma"},
        {"event": "PathMarkedDeadEnd", "path_id": "path_123", "reason": "loop"},
    ]
    with path.open("w", encoding="utf-8") as fh:
        for ev in events:
            fh.write(json.dumps(ev) + "\n")


def test_load_event_data(tmp_path: Path) -> None:
    """The loader should parse NDJSON into a DataFrame."""

    log_path = tmp_path / "events.ndjson"
    _write_events(log_path)

    df = load_event_data(log_path)
    assert list(df["event"]) == [
        "PruneSuggested",
        "TeamMerged",
        "PathMarkedDeadEnd",
    ]


def test_build_collaboration_graph(tmp_path: Path) -> None:
    """Graph construction emits edges when graphviz is available."""

    pytest.importorskip("graphviz")

    log_path = tmp_path / "events.ndjson"
    _write_events(log_path)
    df = load_event_data(log_path)

    graph = build_collaboration_graph(df.to_dict(orient="records"))
    assert graph is not None
    src = graph.source
    assert "team_beta" in src and "team_gamma" in src

