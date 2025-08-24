"""Minimal desktop client for the streaming API.

The client connects to the ``/stream`` endpoint exposed by ``v2/run.py`` and
prints tokens to the terminal as they are received.  When the stream indicates a
new step a simple "step card" header is printed.  If a ``hitl`` (human‑in‑the‑
loop) event is received the user is prompted to confirm the action.

This module is intentionally lightweight and avoids external dependencies so
that it can run in constrained environments used for automated testing.
"""

from __future__ import annotations

import json
from typing import Iterable

import requests


def _iter_events(response: requests.Response) -> Iterable[dict]:
    """Yield parsed JSON events from an SSE ``Response`` object."""

    for line in response.iter_lines():
        if not line:
            continue
        if line.startswith(b"data:"):
            payload = line.split(b":", 1)[1].strip()
            if not payload:
                continue
            try:
                yield json.loads(payload.decode("utf-8"))
            except json.JSONDecodeError:
                continue


def stream_query(query: str, endpoint: str = "http://localhost:8000/stream") -> None:
    """Stream a query to the backend and display live output."""

    with requests.get(endpoint, params={"query": query}, stream=True) as resp:
        resp.raise_for_status()

        for event in _iter_events(resp):
            etype = event.get("type")
            content = event.get("content", "")
            if etype == "token":
                print(content, end=" ", flush=True)
            elif etype == "step":
                print(f"\n[STEP] {content}")
            elif etype == "hitl":
                answer = input(f"{content} (y/n): ")
                if answer.strip().lower() != "y":
                    print("Action aborted by user")
                    break
            elif etype == "done":
                break
        print()


__all__ = ["stream_query"]

