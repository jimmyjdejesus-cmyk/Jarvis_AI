# flake8: noqa
"""
Minimal FastAPI application exposing knowledge graph and mission endpoints.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
import secrets
from typing import Dict, Any, List, Optional, Set
import asyncio

from fastapi import Depends, FastAPI, Header, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field

from .auth import Token, login_for_access_token, role_required
from .knowledge_graph import knowledge_graph
from .galaxy import router as galaxy_router

# Ensure project root is on sys.path when running from the app directory
_app_dir = Path(__file__).resolve().parent
_project_root = _app_dir.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from jarvis.orchestration.mission import Mission, save_mission
from jarvis.orchestration.mission_planner import MissionPlanner
from jarvis.world_model.neo4j_graph import Neo4jGraph
from jarvis.workflows.engine import WorkflowStatus
from jarvis.security.secret_manager import set_secret as set_kv_secret

try:  # Optional import used only for error mapping
    from neo4j.exceptions import ServiceUnavailable  # type: ignore
except Exception:  # pragma: no cover
    class ServiceUnavailable(Exception):  # type: ignore
        pass

app = FastAPI()

# Allow the Vite dev server to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "tauri://localhost",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(galaxy_router)

# Exposed for tests to patch
neo4j_graph = Neo4jGraph()
planner = MissionPlanner(missions_dir=os.path.join("config", "missions"))


class MissionCreate(BaseModel):
    title: str
    goal: str


class CredentialUpdate(BaseModel):
    """Request body for updating service credentials."""

    service: str = Field(
        ..., description="Environment variable name, e.g. OPENAI_API_KEY"
    )
    value: str = Field(..., description="Secret value for the service")


class Neo4jConfig(BaseModel):
    uri: str
    user: str
    password: str


def _require_api_key(x_api_key: str | None) -> None:
    """Enforce API key unless disabled via env.

    Set JARVIS_DISABLE_AUTH=true to bypass checks for local development.
    """
    if str(os.environ.get("JARVIS_DISABLE_AUTH", "")).lower() in {"1", "true", "yes", "on"}:
        return
    api_key = os.environ.get("JARVIS_API_KEY")
    if not api_key or not (x_api_key and secrets.compare_digest(x_api_key, api_key)):
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.post("/token")
async def token(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    """Return an access token for valid credentials."""
    return await login_for_access_token(form_data)


@app.get("/secret", dependencies=[Depends(role_required("admin"))])
def get_secret() -> dict:
    """Protected endpoint requiring an admin role."""
    return {"secret": "classified"}


@app.get("/knowledge/query")
def get_knowledge_query(
    q: str = Query(..., description="Node search"),
) -> dict:
    """Return results from the knowledge graph for the given query."""
    try:
        results = knowledge_graph.query(q)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"results": results}


@app.post("/api/credentials")
def set_credential(payload: CredentialUpdate, x_api_key: str | None = Header(None)) -> dict:
    """Set a runtime credential; restricted by API key.

    Accepts a limited allowlist of services and stores credentials in
    both process environment and the OS keyring (when available).
    """
    _require_api_key(x_api_key)

    allowed = {
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "AZURE_OPENAI_API_KEY",
    }
    if payload.service not in allowed:
        raise HTTPException(status_code=400, detail="Unsupported service")

    # Store in env for immediate availability
    os.environ[payload.service] = payload.value
    # Also persist to keyring when possible
    try:
        set_kv_secret(payload.service, payload.value)
    except Exception:  # pragma: no cover - keyring optional
        pass
    return {"status": "ok"}


@app.post("/api/neo4j/config")
def set_neo4j_config(payload: Neo4jConfig, x_api_key: str | None = Header(None)) -> dict:
    """Configure Neo4j connection using provided credentials.

    Validates the API key, persists the credentials in the OS keyring and
    attempts to initialize a Neo4j driver to verify connectivity.
    """
    _require_api_key(x_api_key)

    # Persist securely
    for k, v in ("NEO4J_URI", payload.uri), ("NEO4J_USER", payload.user), ("NEO4J_PASSWORD", payload.password):
        try:
            set_kv_secret(k, v)
        except Exception:  # pragma: no cover - keyring optional
            pass

    # Reinitialize the shared graph with new credentials
    global neo4j_graph
    try:
        neo4j_graph = Neo4jGraph(uri=payload.uri, user=payload.user, password=payload.password)
    except (ValueError, ServiceUnavailable):
        raise HTTPException(status_code=400, detail="Failed to initialize Neo4j driver")

    return {"status": "ok"}


@app.post("/api/missions", status_code=201)
def create_mission(
    payload: MissionCreate, x_api_key: str | None = Header(None)
) -> Dict[str, str]:
    """Create a new mission and persist its DAG."""
    _require_api_key(x_api_key)
    dag = planner.plan(goal=payload.goal, context={"title": payload.title})
    mission = Mission(
        id=dag.mission_id,
        title=payload.title,
        goal=payload.goal,
        inputs={},
        risk_level="low",
        dag=dag,
    )
    save_mission(mission)
    try:
        neo4j_graph.add_node(
            mission.id,
            "mission",
            {"status": WorkflowStatus.PENDING.value},
        )
    except Exception:  # pragma: no cover - optional graph backend
        pass
    return {
        "mission_id": mission.id,
        "status": WorkflowStatus.PENDING.value,
    }


@app.get("/health")
def get_health() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}


# -----------------------
# Realtime + Workflows (minimal)
# -----------------------

workflows_db: Dict[str, Dict[str, Any]] = {}


class ConnectionManager:
    def __init__(self) -> None:
        self.active: Dict[str, WebSocket] = {}
        self.sessions: Dict[str, Set[str]] = {}

    async def connect(self, ws: WebSocket, client_id: str, session_id: Optional[str] = None) -> None:
        await ws.accept()
        self.active[client_id] = ws
        if session_id:
            self.sessions.setdefault(session_id, set()).add(client_id)

    def disconnect(self, client_id: str) -> None:
        self.active.pop(client_id, None)
        for s in list(self.sessions.values()):
            s.discard(client_id)

    async def send(self, client_id: str, payload: Dict[str, Any]) -> None:
        ws = self.active.get(client_id)
        if ws:
            await ws.send_json(payload)

    async def broadcast_to_session(self, session_id: str, payload: Dict[str, Any]) -> None:
        for cid in self.sessions.get(session_id, set()):
            await self.send(cid, payload)


manager = ConnectionManager()


@app.websocket("/ws/{client_id}")
async def ws_endpoint(websocket: WebSocket, client_id: str, session_id: Optional[str] = Query(None)) -> None:
    await manager.connect(websocket, client_id, session_id)
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                import json as _json

                msg = _json.loads(raw)
            except Exception:
                continue

            mtype = msg.get("type")
            data = msg.get("data", {})

            if mtype == "ping":
                await websocket.send_json({"type": "pong", "timestamp": os.times()[-1]})
            elif mtype == "chat_message":
                # Show quick thinking indicator then echo
                await websocket.send_json({"type": "cerebro_thinking", "data": {"status": "thinking"}})
                await asyncio.sleep(0.4)
                user_msg = data.get("message") if isinstance(data, dict) else data
                await websocket.send_json({"type": "chat_response", "data": {"message": f"Echo: {user_msg}"}})
            elif mtype == "subscribe" and isinstance(data, dict):
                sid = data.get("session_id")
                if sid:
                    manager.sessions.setdefault(sid, set()).add(client_id)
    except WebSocketDisconnect:
        manager.disconnect(client_id)


@app.get("/api/workflow/{session_id}")
def get_workflow(session_id: str) -> Dict[str, Any]:
    wf = workflows_db.get(session_id)
    if wf is None:
        nodes = [
            {"id": "start", "status": "completed"},
            {"id": "analysis-1", "status": "running"},
            {"id": "report-1", "status": "pending"},
        ]
        wf = {"session_id": session_id, "nodes": nodes, "edges": [["start", "analysis-1"], ["analysis-1", "report-1"]]}
        workflows_db[session_id] = wf
    return wf


async def _simulate(session_id: str) -> None:
    wf = get_workflow(session_id)
    nodes: List[Dict[str, Any]] = wf["nodes"]
    await asyncio.sleep(1)
    for n in nodes:
        if n["status"] == "running":
            n["status"] = "completed"
    for n in nodes:
        if n["status"] == "pending":
            n["status"] = "running"
            break
    await manager.broadcast_to_session(session_id, {"type": "workflow_updated", "data": wf})
    await asyncio.sleep(1.5)
    await manager.broadcast_to_session(session_id, {"type": "task_progress", "data": {"progress": 1.0}})


@app.post("/api/workflow/{session_id}/simulate")
async def simulate_workflow(session_id: str) -> Dict[str, Any]:
    asyncio.create_task(_simulate(session_id))
    return {"status": "started"}


if __name__ == "__main__":
    # Run the FastAPI app via Uvicorn when executed directly
    import os as _os
    import uvicorn as _uvicorn

    _host = _os.environ.get("JARVIS_BACKEND_HOST", "127.0.0.1")
    _port = int(_os.environ.get("JARVIS_BACKEND_PORT", "8000"))

    _uvicorn.run(app, host=_host, port=_port)
