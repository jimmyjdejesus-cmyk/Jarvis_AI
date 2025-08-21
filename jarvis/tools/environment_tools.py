"""Environment interaction tools with security checks, logging, and user confirmation."""

import logging
import subprocess
from pathlib import Path
from typing import Optional

from jarvis.auth.security_manager import SecurityManager, get_security_manager
from jarvis.ui.components import ui_components

logger = logging.getLogger(__name__)


def _confirm(message: str) -> bool:
    """Request user confirmation for an action."""
    try:
        return ui_components.confirm_action(message)
    except Exception:
        response = input(f"{message} (y/N): ").strip().lower()
        return response in {"y", "yes"}


def read_file(path: str, username: str,
              security_manager: Optional[SecurityManager] = None) -> Optional[str]:
    """Read a file after permission and user confirmation."""
    sm = security_manager or get_security_manager()
    if not sm.has_path_access(username, path):
        logger.warning("Unauthorized read attempt by %s on %s", username, path)
        if sm.db_manager:
            sm.db_manager.log_security_event(
                username, "READ_DENIED", f"Path: {path}", None, False
            )
        raise PermissionError("Access denied")

    if not _confirm(f"Allow {username} to read {path}?"):
        logger.info("User %s denied read for %s", username, path)
        return None

    try:
        content = Path(path).read_text()
        logger.info("%s read file %s", username, path)
        if sm.db_manager:
            sm.db_manager.log_security_event(
                username, "READ_FILE", f"Path: {path}", None, True
            )
        return content
    except Exception as e:
        logger.error("Error reading file %s: %s", path, e)
        if sm.db_manager:
            sm.db_manager.log_security_event(
                username, "READ_ERROR", f"Path: {path} Error: {e}", None, False
            )
        return None


def write_file(path: str, content: str, username: str,
               security_manager: Optional[SecurityManager] = None) -> bool:
    """Write content to a file after permission and confirmation."""
    sm = security_manager or get_security_manager()
    if not sm.has_path_access(username, path):
        logger.warning("Unauthorized write attempt by %s on %s", username, path)
        if sm.db_manager:
            sm.db_manager.log_security_event(
                username, "WRITE_DENIED", f"Path: {path}", None, False
            )
        raise PermissionError("Access denied")

    if not _confirm(f"Allow {username} to write {path}?"):
        logger.info("User %s denied write for %s", username, path)
        return False

    try:
        Path(path).write_text(content)
        logger.info("%s wrote file %s", username, path)
        if sm.db_manager:
            sm.db_manager.log_security_event(
                username, "WRITE_FILE", f"Path: {path}", None, True
            )
        return True
    except Exception as e:
        logger.error("Error writing file %s: %s", path, e)
        if sm.db_manager:
            sm.db_manager.log_security_event(
                username, "WRITE_ERROR", f"Path: {path} Error: {e}", None, False
            )
        return False


def run_shell_command(command: str, username: str,
                      security_manager: Optional[SecurityManager] = None) -> Optional[str]:
    """Execute a shell command with permission checks and logging."""
    sm = security_manager or get_security_manager()
    if not sm.has_command_access(username, command):
        logger.warning("Unauthorized command attempt by %s: %s", username, command)
        if sm.db_manager:
            sm.db_manager.log_security_event(
                username, "COMMAND_DENIED", f"Command: {command}", None, False
            )
        raise PermissionError("Command not permitted")

    if not _confirm(f"Allow {username} to run '{command}'?"):
        logger.info("User %s denied command '%s'", username, command)
        return None

    try:
        result = subprocess.run(
            shlex.split(command), shell=False, check=True, capture_output=True, text=True
        )
        logger.info("%s executed command '%s'", username, command)
        if sm.db_manager:
            sm.db_manager.log_security_event(
                username, "COMMAND_EXECUTED", f"Command: {command}", None, True
            )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error("Command '%s' failed: %s", command, e)
        if sm.db_manager:
            sm.db_manager.log_security_event(
                username, "COMMAND_ERROR", f"Command: {command} Error: {e}", None, False
            )
        return e.stdout


def run_tests(username: str, security_manager: Optional[SecurityManager] = None,
              command: str = "pytest") -> Optional[str]:
    """Run test suite via shell command with permissions."""
    return run_shell_command(command, username, security_manager)
