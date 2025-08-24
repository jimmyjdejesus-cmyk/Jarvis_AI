"""Run dependency vulnerability scan using pip-audit if available."""

from __future__ import annotations

import subprocess
import sys


def main() -> int:
    try:
        result = subprocess.run([
            sys.executable,
            "-m",
            "pip_audit",
        ], check=False, capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr)
        return result.returncode
    except FileNotFoundError:
        print("pip-audit is not installed. Install it with 'pip install pip-audit'.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
