"""FastAPI server exposing orchestrator operations and event streaming."""
from __future__ import annotations

import asyncio
import json
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse, StreamingResponse

from .orchestrator import MultiAgentOrchestrator
from .message_bus import HierarchicalMessageBus
from agent.logging.scoped_writer import ScopedLogWriter

app = FastAPI(title="Jarvis Orchestrator")
bus = HierarchicalMessageBus()
orchestrator = MultiAgentOrchestrator(mcp_client=None)
_writers: dict[str, ScopedLogWriter] = {}
_last_run_id: str | None = None


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/run")
async def run(state: dict) -> dict:
    """Execute the orchestrator with the provided initial state."""
    run_id = str(uuid.uuid4())
    project_id = state.get("project_id", "default")
    writer = ScopedLogWriter(project_id, run_id)
    _writers[run_id] = writer
    global _last_run_id
    _last_run_id = run_id

    await bus.publish(
        "run.started",
        state,
        scope=run_id,
        run_id=run_id,
        step_id="start",
    )
    result = await orchestrator.run(state)
    await bus.publish(
        "run.finished",
        result,
        scope=run_id,
        run_id=run_id,
        step_id="end",
        parent_id="start",
    )
    return {"run_id": run_id, "result": result}


@app.get("/events/{run_id}")
async def get_events(run_id: str) -> list:
    """Return all events for a given run."""
    return bus.get_scope_events(run_id)


@app.get("/events/{run_id}/stream")
async def stream_events(run_id: str):
    """Stream events for a run using Server-Sent Events."""

    async def event_generator():
        last_idx = 0
        while True:
            events = bus.get_scope_events(run_id)
            for event in events[last_idx:]:
                yield f"data: {json.dumps(event)}\n\n"
            last_idx = len(events)
            await asyncio.sleep(0.1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


async def _log_event(event: dict) -> None:  # type: ignore[arg-type]
    run_id = event.get("run_id")
    if not run_id:
        return
    writer = _writers.get(run_id)
    if not writer:
        return
    payload = event.get("payload")
    writer.log_project(f"{event.get('type')}: {payload}")


bus.subscribe("*", _log_event)


@app.get("/logs/{run_id}")
async def get_logs(run_id: str, q: str | None = None):
    """Return transcript or search results for ``run_id``."""
    actual_id = _last_run_id if run_id == "latest" else run_id
    writer = _writers.get(actual_id) if actual_id else None
    if not writer:
        raise HTTPException(status_code=404, detail="Unknown run")
    if q:
        lines = writer.search(q)
        return PlainTextResponse("\n".join(lines))
    return PlainTextResponse(writer.project_log.read_text(encoding="utf-8"))


__all__ = ["app", "bus", "orchestrator"]
