from __future__ import annotations

"""Scoped logging utilities.

This module provides a :class:`ScopedLogWriter` that writes markdown
transcripts for each project/run combination.  Logs are written under
``logs/projects/<project_id>/runs/<run_id>/`` following the convention
specified in EPIC C.

Only a lightweight feature set is implemented: appending events to
project or team logs, a small in-memory index for queries, secret
redaction, and an export helper used by the UI.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
import re
import time

__all__ = ["ScopedLogWriter"]


def _redact_secrets(text: str) -> str:
    """Best-effort secret redaction.

    Replaces common ``API_KEY=...`` style patterns with ``API_KEY=***`` to
    avoid leaking credentials in transcripts.  The implementation is
    intentionally lightweight and can be extended with additional
    patterns as needed.
    """

    return re.sub(r"(?i)api[_-]?key\s*=\s*\S+", "API_KEY=***", text)


@dataclass
class ScopedLogWriter:
    """Write scoped project and team transcripts.

    Parameters
    ----------
    project_id:
        Identifier for the project whose logs are being recorded.
    run_id:
        Identifier for the current run; defaults to a timestamp for
        convenience.
    base_dir:
        Root directory under which all log folders will be created.
    """

    project_id: str
    run_id: str = field(default_factory=lambda: str(int(time.time())))
    base_dir: Path = Path("logs")

    def __post_init__(self) -> None:
        self.run_dir = self.base_dir / "projects" / self.project_id / "runs" / self.run_id
        self.project_log = self.run_dir / "agent_project.md"
        self._index: Dict[str, List[str]] = {}
        self.project_log.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Logging helpers
    # ------------------------------------------------------------------
    def _write(self, path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        cleaned = _redact_secrets(text)
        with path.open("a", encoding="utf-8") as f:
            f.write(cleaned + "\n")
        self._index.setdefault(str(path), []).append(cleaned)

    def log_project(self, message: str) -> Path:
        """Append a message to the project transcript."""
        self._write(self.project_log, message)
        return self.project_log

    def log_team(self, team_id: str, message: str) -> Path:
        """Append a message to a team transcript."""
        team_log = self.run_dir / "teams" / team_id / "agent_team.md"
        self._write(team_log, message)
        return team_log

    # Convenience methods for common events ---------------------------------
    def log_prompt(self, prompt: str, model: str, tokens: int, team_id: Optional[str] = None) -> None:
        entry = f"## Prompt\nmodel: {model}\ntokens: {tokens}\n{prompt}"
        if team_id:
            self.log_team(team_id, entry)
        else:
            self.log_project(entry)

    def log_tool_call(self, tool: str, args: Dict[str, str], team_id: Optional[str] = None) -> None:
        entry = f"## Tool Call\ntool: {tool}\nargs: {args}"
        if team_id:
            self.log_team(team_id, entry)
        else:
            self.log_project(entry)

    def log_final_synthesis(self, content: str) -> None:
        self.log_project(f"## Final\n{content}")

    # ------------------------------------------------------------------
    # Query & export helpers
    # ------------------------------------------------------------------
    def search(self, query: str, path: Optional[Path] = None) -> List[str]:
        """Return log lines that contain ``query``.

        Parameters
        ----------
        query:
            Case-insensitive substring to look for.
        path:
            Optional specific log file to restrict the search to.
        """

        targets = [str(path)] if path else list(self._index.keys())
        results: List[str] = []
        for p in targets:
            for line in self._index.get(p, []):
                if query.lower() in line.lower():
                    results.append(line)
        return results

    def export_transcript(self) -> Path:
        """Return the path to the project transcript for download."""
        return self.project_log
