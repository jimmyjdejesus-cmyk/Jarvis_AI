"""
Launcher to run the newer Jarvis AI PyQt GUI from the legacy workspace.

Prereq: install the newer repo in editable mode so the `jarvis` package is importable.

Example:
    pip install -e "C:\\Users\\Student\\Downloads\\github_repos\\jarvis-ai"

You can set OLLAMA_* env vars to control local model host/model.
"""

import os
import sys


def _ensure_new_repo_on_path() -> None:
    """Best-effort: append the newer repo path to sys.path if not installed.

    This allows running without installing, useful during development.
    """
    candidates = [
        os.path.join(
            os.path.expanduser("~"),
            "Downloads",
            "github_repos",
            "jarvis-ai",
        )
    ]
    for path in candidates:
        if os.path.isdir(path) and path not in sys.path:
            sys.path.insert(0, path)


def main() -> None:
    _ensure_new_repo_on_path()
    try:
        from jarvis.gui.main_window import run_jarvis_gui
    except Exception as exc:
        sys.stderr.write(
            "Failed to import new GUI (jarvis.gui).\n"
            "Ensure the newer repo is installed:\n"
            "    pip install -e \"C:\\Users\\Student\\Downloads\\github_repos\\jarvis-ai\"\n"
            f"Error: {exc}\n"
        )
        raise SystemExit(1)

    # Sensible defaults for local Ollama if not provided
    os.environ.setdefault("OLLAMA_HOST", "http://localhost:11434")
    os.environ.setdefault("OLLAMA_MODEL", "llama3.1:8b-instruct-q4_K_M")

    run_jarvis_gui()


if __name__ == "__main__":
    main()


