"""A simple sandbox for executing Python code."""

import subprocess
import tempfile
import os
from dataclasses import dataclass

@dataclass
class ExecutionResult:
    """The result of a code execution."""
    stdout: str
    stderr: str
    exit_code: int

def run_python_code(code: str, timeout: int = 10) -> ExecutionResult:
    """
    Executes a string of Python code in a sandbox and returns the result.

    Args:
        code: The Python code to execute.
        timeout: The timeout in seconds for the execution.

    Returns:
        An ExecutionResult object with the stdout, stderr, and exit code.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
        tmp.write(code)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            ["python", tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return ExecutionResult(
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.returncode,
        )
    except subprocess.TimeoutExpired:
        return ExecutionResult(
            stdout="",
            stderr=f"Execution timed out after {timeout} seconds.",
            exit_code=1,
        )
    finally:
        os.unlink(tmp_path)
