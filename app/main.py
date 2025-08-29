"""
Minimal FastAPI application exposing knowledge graph and mission endpoints.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
import secrets
from typing import Dict

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field

from .auth import Token, login_for_access_token, role_required
from .knowledge_graph import knowledge_graph

# Ensure project root is on sys.path when running from the app directory
_app_dir = Path(__file__).resolve().parent
_project_root = _app_dir.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from jarvis.orchestration.mission import Mission, save_mission
from jarvis.orchestration.mission_planner import MissionPlanner
from jarvis.world_model.neo4j_graph import Neo4jGraph
from jarvis.workflows.engine import WorkflowStatus

app = FastAPI()

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


@app.post("/api/missions", status_code=201)
def create_mission(
    payload: MissionCreate, x_api_key: str = Header(...)
) -> Dict[str, str]:
    """Create a new mission and persist its DAG."""
    if not (api_key := os.environ.get("JARVIS_API_KEY")) or not secrets.compare_digest(x_api_key, api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
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


if __name__ == "__main__":
    # Run the FastAPI app via Uvicorn when executed directly
    import os as _os
    import uvicorn as _uvicorn

    _host = _os.environ.get("JARVIS_BACKEND_HOST", "127.0.0.1")
    _port = int(_os.environ.get("JARVIS_BACKEND_PORT", "8000"))

    _uvicorn.run(app, host=_host, port=_port)
