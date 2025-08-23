"""Analytics dashboard for the Jarvis AI UI.

This module reads the event log and visualises real agent activity.
Metrics are derived from ``logs/events.ndjson`` while an optional
Graphviz graph exposes how the orchestrator and specialists collaborate
on tasks.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set

import pandas as pd
import streamlit as st

try:  # Optional dependency for graph rendering
    from graphviz import Digraph
except Exception:  # pragma: no cover - graphviz is optional
    Digraph = None  # type: ignore


EVENT_LOG = Path("logs/events.ndjson")


def load_event_data(path: str | Path = EVENT_LOG) -> pd.DataFrame:
    """Load NDJSON event records into a DataFrame.

    Parameters
    ----------
    path:
        Location of the event log.  Missing files yield an empty
        ``DataFrame``.
    """

    p = Path(path)
    if not p.exists():
        return pd.DataFrame()

    records: List[Dict[str, Any]] = []
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return pd.DataFrame.from_records(records)


def build_collaboration_graph(events: Iterable[Dict[str, Any]]) -> Optional[Digraph]:
    """Create a Graphviz visualisation of agent collaboration.

    ``TeamMerged`` events produce edges between teams while pruning or
    dead-end markers are displayed as coloured nodes.  When Graphviz is
    unavailable ``None`` is returned.
    """

    if Digraph is None:
        return None

    dot = Digraph(comment="agent_collaboration")
    for ev in events:
        event_type = ev.get("event")
        if event_type == "TeamMerged":
            src = ev.get("source")
            tgt = ev.get("target")
            if src and tgt:
                dot.edge(str(src), str(tgt), label="merged")
        elif event_type == "PruneSuggested":
            team = ev.get("team_id")
            if team:
                dot.node(str(team), str(team), color="orange", style="filled")
        elif event_type == "PathMarkedDeadEnd":
            path_id = ev.get("path_id")
            if path_id:
                dot.node(str(path_id), str(path_id), color="red", style="filled")
    return dot


def render_analytics_dashboard(path: str | Path = EVENT_LOG) -> None:  # pragma: no cover - UI rendering
    """Render analytics and collaboration visualisations in Streamlit."""

    st.subheader("\ud83d\udcca Analytics Dashboard")
    df = load_event_data(path)
    if df.empty:
        st.info("No agent activity recorded.")
        return

    # Basic metrics
    teams: Set[str] = set(df.get("team_id", []))
    teams |= set(df.get("source", []))
    teams |= set(df.get("target", []))
    teams.discard(None)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Events", str(len(df)))
    with col2:
        st.metric("Teams", str(len(teams)))
    with col3:
        dead_ends = int((df.get("event") == "PathMarkedDeadEnd").sum())
        st.metric("Dead Ends", str(dead_ends))

    # Event type distribution
    counts = df["event"].value_counts().reset_index()
    counts.columns = ["event", "count"]
    st.bar_chart(counts.set_index("event"))

    # Collaboration graph
    graph = build_collaboration_graph(df.to_dict(orient="records"))
    if graph is not None:
        st.graphviz_chart(graph.source, use_container_width=True)


__all__ = [
    "render_analytics_dashboard",
    "load_event_data",
    "build_collaboration_graph",
]

