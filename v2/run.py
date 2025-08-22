"""FastAPI application exposing Jarvis V2 functionality.

This small server is intentionally lightweight – it simply exposes a standard
HTTP endpoint for normal requests and a streaming endpoint using Server Sent
Events (SSE).  The streaming endpoint allows desktop and web frontends to
receive tokens as they are produced by the agent.
"""

from __future__ import annotations

import json
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import (
    StreamingResponse,
    PlainTextResponse,
    Response,
)

from v2.agent.core.agent import JarvisAgentV2
from v2.config.config import DEFAULT_CONFIG
from v2.agent.adapters.langgraph_ui import visualizer


app = FastAPI(title="Jarvis V2 API")

# Instantiate the agent once at startup
agent = JarvisAgentV2(config=DEFAULT_CONFIG)
agent.setup_workflow()


@app.get("/")
async def root(query: str) -> dict:
    """Run the workflow and return the final response."""

    return agent.run_workflow(query)


async def _event_stream(query: str) -> AsyncGenerator[str, None]:
    """Internal helper that converts agent events to SSE formatted strings."""

    async for event in agent.stream_workflow(query):
        yield f"data: {json.dumps(event)}\n\n"


@app.get("/stream")
async def stream(query: str) -> StreamingResponse:
    """Stream workflow execution using Server‑Sent Events."""

    return StreamingResponse(_event_stream(query), media_type="text/event-stream")


@app.get("/graph/export")
async def export_graph(format: str = "json"):
    """Export the current workflow graph."""

    data = visualizer.export(format)
    if format == "png":
        return Response(content=data, media_type="image/png")
    if format == "dot":
        return PlainTextResponse(data)
    return data


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

