#!/usr/bin/env python3
"""Populate the vector memory store from legacy JSON user memory."""

import glob
import json
import os
from typing import Any

from jarvis.memory import ProjectMemory


def migrate(user_memory_dir: str = "user_memory", project: str = "default") -> None:
    """Migrate all ``*.json`` files into the Chroma-backed memory store."""
    memory = ProjectMemory()
    pattern = os.path.join(user_memory_dir, "*.json")
    for path in glob.glob(pattern):
        session = os.path.splitext(os.path.basename(path))[0]
        with open(path, "r", encoding="utf-8") as f:
            data: Any = json.load(f)
        for entry in data.get("preference_history", []):
            text = json.dumps(entry, ensure_ascii=False)
            memory.add(project, session, text, {"type": entry.get("type")})


if __name__ == "__main__":  # pragma: no cover - script entry point
    migrate()
