from __future__ import annotations

import secrets
import os
from typing import Dict

from fastapi import FastAPI, Header, HTTPException

from pydantic import BaseModel, Field

from jarvis.orchestration.mission import Mission, save_mission, load_mission
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