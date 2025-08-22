"""Simple FastAPI server exposing orchestrator operations.

This server is intentionally lightweight – it provides a health endpoint and
an endpoint to execute a workflow state through the ``MultiAgentOrchestrator``.
"""
from __future__ import annotations

from fastapi import FastAPI

from .orchestrator import MultiAgentOrchestrator

app = FastAPI(title="Jarvis Orchestrator")
orchestrator = MultiAgentOrchestrator(mcp_client=None)


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/run")
async def run(state: dict) -> dict:
    """Execute the orchestrator with the provided initial state."""
    result = await orchestrator.run(state)
    return result
