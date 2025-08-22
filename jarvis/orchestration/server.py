"""FastAPI server exposing orchestrator operations and event streaming."""
from __future__ import annotations

import asyncio
import json
import uuid

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from .orchestrator import MultiAgentOrchestrator
from .message_bus import MessageBus

app = FastAPI(title="Jarvis Orchestrator")
bus = MessageBus()
orchestrator = MultiAgentOrchestrator(mcp_client=None)


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/run")
async def run(state: dict) -> dict:
    """Execute the orchestrator with the provided initial state."""
    run_id = str(uuid.uuid4())
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


__all__ = ["app", "bus", "orchestrator"]
