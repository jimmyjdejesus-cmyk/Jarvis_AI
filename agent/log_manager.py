"""Utilities for scoped agent logging and querying."""
from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Optional
import re

from .guardrails import confirm_destructive_action

# Global project log path
PROJECT_LOG = Path(__file__).resolve().parent.parent / "agent_project.md"

def _append_line(path: Path, message: str) -> None:
    """Append a markdown bullet line to the given file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(f"- {message}\n")

def append_team_log(team_dir: Path, message: str) -> Path:
    """Append a message to the team-specific log.

    Args:
        team_dir: Directory representing the team's scope.
        message: Message to log.
    Returns:
        Path to the team log file.
    """
    log_path = Path(team_dir) / "agent_team.md"
    confirm_destructive_action(f"write to {log_path}")
    _append_line(log_path, message)
    return log_path

def append_project_log(message: str) -> Path:
    """Append a message to the global project log."""
    confirm_destructive_action(f"write to {PROJECT_LOG}")
    _append_line(PROJECT_LOG, message)
    return PROJECT_LOG

def query_logs(query: str, team_dir: Optional[Path] = None) -> List[Dict[str, str]]:
    """Search project and optionally team logs for a query.

    Args:
        query: Text to search for.
        team_dir: Optional team directory to include in search.
    Returns:
        List of dicts with file path, line number, and content.
    """
    files = [PROJECT_LOG]
    if team_dir is not None:
        team_log = Path(team_dir) / "agent_team.md"
        if team_log.exists():
            files.append(team_log)
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    results: List[Dict[str, str]] = []
    for file in files:
        if not file.exists():
            continue
        with file.open("r", encoding="utf-8") as f:
            for i, line in enumerate(f, start=1):
                if pattern.search(line):
                    results.append({
                        "file": str(file),
                        "line": i,
                        "content": line.strip(),
                    })
    return results
