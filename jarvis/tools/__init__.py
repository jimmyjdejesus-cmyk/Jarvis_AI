"""Utility and web tools for Jarvis AI.

This package exposes common tooling used across the Jarvis ecosystem,
including web research capabilities.
"""

from .repository_indexer import RepositoryIndexer
from .environment_tools import read_file, write_file, run_shell_command, run_tests
from .web_tools import WebSearchTool, WebReaderTool
from .legacy_wrappers import (
    safe_read_file,
    safe_write_file,
    safe_run_shell_command,
    set_filesystem_policy,
)

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
]
