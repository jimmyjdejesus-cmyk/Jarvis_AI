"""Utility and web tools for Jarvis AI.

This package exposes common tooling used across the Jarvis ecosystem,
including web research capabilities.
"""

try:  # Optional dependency
    from .repository_indexer import RepositoryIndexer
except Exception:  # pragma: no cover - optional feature
    RepositoryIndexer = None  # type: ignore
from .environment_tools import read_file, write_file, run_shell_command, run_tests
try:  # Optional dependency
    from .web_tools import WebSearchTool, WebReaderTool
except Exception:  # pragma: no cover - optional feature
    WebSearchTool = WebReaderTool = None  # type: ignore

from .legacy_wrappers import (
    safe_read_file,
    safe_write_file,
    safe_run_shell_command,
    set_filesystem_policy,
)
from .ide import open_file, save_file
from .notes import add_note, list_notes
from .github import create_issue
from .fs_safety import ensure_path_is_allowed, safe_read, safe_write
from .git_sandbox import run_git_command, sanitize_git_args

__all__ = [
    "RepositoryIndexer",
    "read_file",
    "write_file",
    "run_shell_command",
    "run_tests",
    "WebSearchTool",
    "WebReaderTool",
    "safe_read_file",
    "safe_write_file",
    "safe_run_shell_command",
    "set_filesystem_policy",
    "open_file",
    "save_file",
    "add_note",
    "list_notes",
    "create_issue",
    "ensure_path_is_allowed",
    "safe_read",
    "safe_write",
    "run_git_command",
    "sanitize_git_args",
]
