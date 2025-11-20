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

from fastapi import Depends, FastAPI, Header, HTTPException, Query, WebSocket, WebSocketDisconnect, APIRouter
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from dotenv import load_dotenv

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
from jarvis.agent_bridge import initialize_agent_bridge, get_agent_bridge
from jarvis.memory_bridge import initialize_memory_bridge, get_memory_bridge
from jarvis.workflow_bridge import initialize_workflow_bridge, get_workflow_bridge
from jarvis.security_bridge import initialize_security_bridge, get_security_bridge
from jarvis.monitoring_bridge import initialize_monitoring_bridge, get_monitoring_bridge

try:  # Optional import used only for error mapping
    from neo4j.exceptions import ServiceUnavailable  # type: ignore
except Exception:  # pragma: no cover
    class ServiceUnavailable(Exception):  # type: ignore
        pass

# Load environment variables early (.env in project root or CWD)
try:
    load_dotenv()
except Exception:
    pass

app = FastAPI()
from jarvis.core.mcp_agent import MCPJarvisAgent

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

# Versioned API router (secured by default via API key)
# NOTE: For local dev we're not attaching the auth dependency to the entire router
# to avoid import-time issues. Individual endpoints still call _require_api_key where necessary.
api_v1 = APIRouter(prefix="/api/v1", tags=["api-v1"])

# -----------------------
# Bridge to new runtime (OllamaClient)
# -----------------------
try:
    # Newer repo runtime
    from jarvis.config.config import config as new_config  # type: ignore
    from jarvis.core.ollama_client import OllamaClient as NewOllamaClient  # type: ignore
    from jarvis.core.ollama_client import ChatMessage as NewChatMessage  # type: ignore
    from jarvis.core.agent_manager import AgentManager as NewAgentManager  # type: ignore
    from jarvis.core.memory import ConversationMemory as NewConversationMemory  # type: ignore
    from jarvis.core.memory import KnowledgeGraph as NewKnowledgeGraph  # type: ignore
    _new_runtime_available = True
except Exception:  # pragma: no cover - optional bridge
    new_config = None
    NewOllamaClient = None  # type: ignore
    NewChatMessage = None  # type: ignore
    NewAgentManager = None  # type: ignore
    NewConversationMemory = None  # type: ignore
    NewKnowledgeGraph = None  # type: ignore
    _new_runtime_available = False

# Initialize new runtime components
new_ollama_client = None
new_agent_manager = None
new_conversation_memory = None
new_knowledge_graph = None

if _new_runtime_available:
    try:
        new_ollama_client = NewOllamaClient()
        new_conversation_memory = NewConversationMemory()
        new_knowledge_graph = NewKnowledgeGraph()
        new_agent_manager = NewAgentManager(
            ollama_client=new_ollama_client,
            memory=new_conversation_memory,
            knowledge_graph=new_knowledge_graph
        )
        
        # Initialize bridges
        initialize_agent_bridge(new_agent_manager, new_ollama_client)
        initialize_memory_bridge(new_conversation_memory, new_knowledge_graph)
        initialize_workflow_bridge(new_agent_manager, new_knowledge_graph)
        initialize_security_bridge(new_agent_manager)
        initialize_monitoring_bridge(new_agent_manager, new_ollama_client)
        
    except Exception as e:
        print(f"Warning: Failed to initialize new runtime: {e}")
        new_ollama_client = None
        new_agent_manager = None
        new_conversation_memory = None
        new_knowledge_graph = None


class MissionCreate(BaseModel):
    title: str
    goal: str


class CredentialUpdate(BaseModel):
    """Request body for updating service credentials."""

    service: str = Field(
        ..., description="Environment variable name, e.g. OPENAI_API_KEY"
    )
    value: str = Field(..., description="Secret value for the service")


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    model: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    stream: bool = False


# -----------------------
# v1 Schemas
# -----------------------

class HealthResponse(BaseModel):
    status: str
    ollama: str | None = None


class ModelsResponse(BaseModel):
    models: list[str]


class ChatResponse(BaseModel):
    content: str
    model: str | None = None


class AgentsListResponse(BaseModel):
    agents: list[str]
    count: int


# -----------------------
# v1 Feed + Jobs Schemas
# -----------------------

class FeedItem(BaseModel):
    id: str | None = None
    source: str | None = None
    content: str
    metadata: Dict[str, Any] | None = None


class FeedIngestRequest(BaseModel):
    items: list[FeedItem]
    persist_to_knowledge: bool = True
    persist_to_memory: bool = True


class FeedIngestResponse(BaseModel):
    ingested: int
    errors: int


class JobRequest(BaseModel):
    mode: str = Field(..., description="chat | agent | workflow")
    payload: Dict[str, Any] = Field(default_factory=dict)
    callback_url: str | None = Field(default=None, description="Optional HTTP callback for result")


class JobResponse(BaseModel):
    job_id: str
    status: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    result: Dict[str, Any] | None = None


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


def _require_api_key_dep(x_api_key: str | None = Header(None)) -> None:
    """FastAPI dependency wrapper for API key enforcement."""
    _require_api_key(x_api_key)


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


@api_v1.get("/health", response_model=HealthResponse, summary="Health check", description="Returns overall system health and Ollama status if available.")
def v1_get_health() -> HealthResponse:
    """Health check endpoint."""
    status = {"status": "ok"}
    if _new_runtime_available:
        try:
            healthy = new_ollama_client.health_check() if new_ollama_client else False
            status["ollama"] = "ok" if healthy else "unavailable"
        except Exception:
            status["ollama"] = "error"
    return HealthResponse(**status)


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
                # Stream via new runtime if available, else echo
                user_msg = data.get("message") if isinstance(data, dict) else data
                await websocket.send_json({"type": "cerebro_thinking", "data": {"status": "thinking"}})
                if _new_runtime_available and new_ollama_client is not None and NewChatMessage is not None:
                    try:
                        messages = [
                            NewChatMessage(role="system", content="You are Jarvis, a helpful local assistant."),
                            NewChatMessage(role="user", content=str(user_msg)),
                        ]
                        gen = new_ollama_client.chat(messages, stream=True)
                        async def _stream():
                            for chunk in gen:
                                if chunk and getattr(chunk, "content", ""):
                                    yield {"type": "chat_delta", "data": {"delta": chunk.content}}
                            yield {"type": "chat_done", "data": {"done": True}}
                        async for item in _stream():
                            await websocket.send_json(item)
                    except Exception:
                        await websocket.send_json({"type": "chat_response", "data": {"message": f"Echo: {user_msg}"}})
                else:
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


# -----------------------
# Bridged endpoints to new runtime
# -----------------------

@api_v1.get("/models", response_model=ModelsResponse, summary="List LLM models", description="Lists available models from the new Ollama runtime.")
def v1_list_models() -> ModelsResponse:
    """List available models from new runtime if available."""
    if not (_new_runtime_available and new_ollama_client):
        raise HTTPException(status_code=503, detail="New runtime unavailable")
    try:
        models = new_ollama_client.get_available_models()
        return ModelsResponse(models=models)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to list models: {exc}")


@api_v1.get("/agents", response_model=AgentsListResponse)
def v1_list_agents() -> AgentsListResponse:
    """List available agents from new runtime."""
    if not (_new_runtime_available and new_agent_manager):
        raise HTTPException(status_code=503, detail="New runtime unavailable")
    try:
        agents = list(new_agent_manager.agents.keys())
        return AgentsListResponse(agents=agents, count=len(agents))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to list agents: {exc}")


@app.get("/api/agents/{agent_id}/status")
def get_agent_status(agent_id: str) -> Dict[str, Any]:
    """Get status of a specific agent."""
    if not (_new_runtime_available and new_agent_manager):
        raise HTTPException(status_code=503, detail="New runtime unavailable")
    try:
        status = new_agent_manager.get_agent_status(agent_id)
        if status is None:
            raise HTTPException(status_code=404, detail="Agent not found")
        return {"agent_id": agent_id, "status": status.value}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to get agent status: {exc}")


@app.get("/api/memory/conversations")
def get_conversations() -> Dict[str, Any]:
    """Get recent conversations from memory."""
    if not (_new_runtime_available and new_conversation_memory):
        raise HTTPException(status_code=503, detail="New runtime unavailable")
    try:
        conversations = new_conversation_memory.get_recent_conversations(10)
        return {"conversations": conversations, "count": len(conversations)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to get conversations: {exc}")


@app.get("/api/knowledge/search")
def search_knowledge(q: str = Query(..., description="Search query")) -> Dict[str, Any]:
    """Search knowledge graph."""
    if not (_new_runtime_available and new_knowledge_graph):
        raise HTTPException(status_code=503, detail="New runtime unavailable")
    try:
        results = new_knowledge_graph.search(q)
        return {"query": q, "results": results}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to search knowledge: {exc}")


class AgentTaskRequest(BaseModel):
    """Request to execute an agent task."""
    agent_type: str
    objective: str
    context: Dict[str, Any] = {}
    priority: int = 1
    timeout: int = 300


class CollaborationRequest(BaseModel):
    """Request for agent collaboration."""
    agent_types: List[str]
    objective: str
    context: Dict[str, Any] = {}


@api_v1.post("/agents/execute", summary="Execute agent task", description="Executes a single task using the specified logical agent type (e.g., research, coding).")
async def v1_execute_agent_task(request: AgentTaskRequest) -> Dict[str, Any]:
    """Execute a task using the new agent system."""
    bridge = get_agent_bridge()
    if not bridge:
        raise HTTPException(status_code=503, detail="Agent bridge not available")
    
    try:
        from jarvis.agent_bridge import LegacyAgentTask
        import uuid
        
        task = LegacyAgentTask(
            task_id=str(uuid.uuid4()),
            agent_type=request.agent_type,
            objective=request.objective,
            context=request.context,
            priority=request.priority,
            timeout=request.timeout
        )
        
        result = await bridge.execute_legacy_task(task)
        return result
        
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to execute agent task: {exc}")


@api_v1.post("/agents/collaborate", summary="Agent collaboration", description="Initiates a collaboration between multiple logical agent types.")
async def v1_execute_collaboration(request: CollaborationRequest) -> Dict[str, Any]:
    """Execute a collaboration between multiple agents."""
    bridge = get_agent_bridge()
    if not bridge:
        raise HTTPException(status_code=503, detail="Agent bridge not available")
    
    try:
        result = await bridge.execute_collaboration(
            agent_types=request.agent_types,
            objective=request.objective,
            context=request.context
        )
        return result
        
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to execute collaboration: {exc}")


@api_v1.get("/agents/capabilities/{agent_type}", summary="Agent capabilities", description="Returns capabilities and status for a given logical agent type.")
async def v1_get_agent_capabilities(agent_type: str) -> Dict[str, Any]:
    """Get capabilities of a specific agent type."""
    bridge = get_agent_bridge()
    if not bridge:
        raise HTTPException(status_code=503, detail="Agent bridge not available")
    
    try:
        result = await bridge.get_agent_capabilities(agent_type)
        return result
        
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to get agent capabilities: {exc}")


@api_v1.get("/agents/bridge/list", summary="List registered agents", description="Lists currently registered agents with status and capabilities.")
async def v1_list_bridge_agents() -> Dict[str, Any]:
    """List all agents available through the bridge."""
    bridge = get_agent_bridge()
    if not bridge:
        raise HTTPException(status_code=503, detail="Agent bridge not available")
    
    try:
        agents = await bridge.list_available_agents()
        return {"agents": agents, "count": len(agents)}
        
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to list bridge agents: {exc}")


# Memory bridge endpoints
@api_v1.post("/memory/sync/to-legacy", summary="Export conversations to legacy", description="Exports recent conversations from the new memory system to legacy JSON artifacts.")
def v1_sync_memory_to_legacy() -> Dict[str, Any]:
    """Sync new memory systems to legacy format."""
    bridge = get_memory_bridge()
    if not bridge:
        raise HTTPException(status_code=503, detail="Memory bridge not available")
    
    try:
        result = bridge.sync_conversations_to_legacy()
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to sync memory to legacy: {exc}")


@api_v1.post("/memory/sync/from-legacy", summary="Import legacy conversations", description="Imports legacy conversation JSON files into the new memory system.")
def v1_sync_memory_from_legacy() -> Dict[str, Any]:
    """Load legacy memory data into new system."""
    bridge = get_memory_bridge()
    if not bridge:
        raise HTTPException(status_code=503, detail="Memory bridge not available")
    
    try:
        result = bridge.load_legacy_conversations()
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to sync memory from legacy: {exc}")


@api_v1.get("/memory/stats", summary="Memory statistics", description="Returns a summary of new and legacy memory state.")
def v1_get_memory_stats() -> Dict[str, Any]:
    """Get memory system statistics."""
    bridge = get_memory_bridge()
    if not bridge:
        raise HTTPException(status_code=503, detail="Memory bridge not available")
    
    try:
        stats = bridge.get_memory_stats()
        return stats
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to get memory stats: {exc}")


@api_v1.post("/memory/migrate", summary="Run memory migration", description="Runs export new->legacy, import legacy->new, and returns a summary.")
def v1_migrate_all_memory() -> Dict[str, Any]:
    """Migrate all memory data between systems."""
    bridge = get_memory_bridge()
    if not bridge:
        raise HTTPException(status_code=503, detail="Memory bridge not available")
    
    try:
        result = bridge.migrate_all_data()
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to migrate memory: {exc}")


# Workflow bridge endpoints
class WorkflowTaskRequest(BaseModel):
    """Request to execute a workflow task."""
    workflow_type: str
    parameters: Dict[str, Any] = {}
    priority: int = 1
    timeout: int = 600


@api_v1.post("/workflows/execute", summary="Execute workflow", description="Executes a research/analysis/benchmark workflow using the new runtime.")
async def v1_execute_workflow_task(request: WorkflowTaskRequest) -> Dict[str, Any]:
    """Execute a workflow task using the new system."""
    bridge = get_workflow_bridge()
    if not bridge:
        raise HTTPException(status_code=503, detail="Workflow bridge not available")
    
    try:
        from jarvis.workflow_bridge import LegacyWorkflowTask
        import uuid
        
        task = LegacyWorkflowTask(
            task_id=str(uuid.uuid4()),
            workflow_type=request.workflow_type,
            parameters=request.parameters,
            priority=request.priority,
            timeout=request.timeout
        )
        
        result = await bridge.execute_workflow(task)
        return result
        
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to execute workflow: {exc}")


@api_v1.get("/workflows/capabilities", summary="Workflow capabilities", description="Returns available workflows and their parameters.")
async def v1_get_workflow_capabilities() -> Dict[str, Any]:
    """Get available workflow capabilities."""
    bridge = get_workflow_bridge()
    if not bridge:
        raise HTTPException(status_code=503, detail="Workflow bridge not available")
    
    try:
        capabilities = await bridge.get_workflow_capabilities()
        return capabilities
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to get workflow capabilities: {exc}")


@api_v1.get("/workflows/active", summary="List active workflows", description="Lists active collaborations tracked by the AgentManager.")
async def v1_list_active_workflows() -> Dict[str, Any]:
    """List currently active workflows."""
    bridge = get_workflow_bridge()
    if not bridge:
        raise HTTPException(status_code=503, detail="Workflow bridge not available")
    
    try:
        workflows = await bridge.list_active_workflows()
        return {"workflows": workflows, "count": len(workflows)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to list active workflows: {exc}")


# Security bridge endpoints
class SecurityValidationRequest(BaseModel):
    """Request to validate an agent action."""
    agent_id: str
    action: str
    context: Dict[str, Any] = {}


@api_v1.post("/security/validate", summary="Validate agent action", description="Runs basic runtime checks on an agent action and context.")
def v1_validate_agent_action(request: SecurityValidationRequest) -> Dict[str, Any]:
    """Validate an agent action using security systems."""
    bridge = get_security_bridge()
    if not bridge:
        raise HTTPException(status_code=503, detail="Security bridge not available")
    
    try:
        result = bridge.validate_agent_action(
            agent_id=request.agent_id,
            action=request.action,
            context=request.context
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to validate action: {exc}")


@api_v1.get("/security/events", summary="Security events", description="Returns recent security validation events.")
def v1_get_security_events(limit: int = 100) -> Dict[str, Any]:
    """Get recent security events."""
    bridge = get_security_bridge()
    if not bridge:
        raise HTTPException(status_code=503, detail="Security bridge not available")
    
    try:
        events = bridge.get_security_events(limit)
        return {"events": events, "count": len(events)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to get security events: {exc}")


@api_v1.get("/security/stats", summary="Security stats", description="Returns aggregate security counters and rates.")
def v1_get_security_stats() -> Dict[str, Any]:
    """Get security statistics."""
    bridge = get_security_bridge()
    if not bridge:
        raise HTTPException(status_code=503, detail="Security bridge not available")
    
    try:
        stats = bridge.get_security_stats()
        return stats
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to get security stats: {exc}")


@api_v1.post("/security/audit", summary="Run security audit", description="Runs a summary audit across agent health and recent security events.")
def v1_run_security_audit() -> Dict[str, Any]:
    """Run a comprehensive security audit."""
    bridge = get_security_bridge()
    if not bridge:
        raise HTTPException(status_code=503, detail="Security bridge not available")
    
    try:
        audit = bridge.run_security_audit()
        return audit
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to run security audit: {exc}")


# Monitoring bridge endpoints
@api_v1.get("/monitoring/metrics", summary="Collect metrics", description="Collects a batch of system and runtime metrics and returns them.")
def v1_get_system_metrics() -> Dict[str, Any]:
    """Get current system metrics."""
    bridge = get_monitoring_bridge()
    if not bridge:
        raise HTTPException(status_code=503, detail="Monitoring bridge not available")
    
    try:
        metrics = bridge.collect_system_metrics()
        return {"metrics": [{"name": m.name, "value": m.value, "unit": m.unit, "timestamp": m.timestamp} for m in metrics]}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {exc}")


@api_v1.get("/monitoring/summary", summary="Metrics summary", description="Aggregates metrics over a time window and returns basic statistics.")
def v1_get_metrics_summary(time_window_minutes: int = 60) -> Dict[str, Any]:
    """Get metrics summary for specified time window."""
    bridge = get_monitoring_bridge()
    if not bridge:
        raise HTTPException(status_code=503, detail="Monitoring bridge not available")
    
    try:
        summary = bridge.get_metrics_summary(time_window_minutes)
        return summary
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics summary: {exc}")


@api_v1.get("/monitoring/health", summary="System health", description="Returns a coarse-grained health report across components and host.")
def v1_get_health_status() -> Dict[str, Any]:
    """Get overall system health status."""
    bridge = get_monitoring_bridge()
    if not bridge:
        raise HTTPException(status_code=503, detail="Monitoring bridge not available")
    
    try:
        health = bridge.get_health_status()
        return health
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to get health status: {exc}")


@api_v1.get("/monitoring/performance", summary="Performance trends", description="Returns simple trend analysis for key metrics in the last hour.")
def v1_get_performance_metrics() -> Dict[str, Any]:
    """Get performance metrics and trends."""
    bridge = get_monitoring_bridge()
    if not bridge:
        raise HTTPException(status_code=503, detail="Monitoring bridge not available")
    
    try:
        performance = bridge.get_performance_metrics()
        return performance
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {exc}")


@api_v1.get("/monitoring/export", summary="Export metrics", description="Exports current metrics history (JSON only).")
def v1_export_metrics(format: str = "json") -> Dict[str, Any]:
    """Export metrics in specified format."""
    bridge = get_monitoring_bridge()
    if not bridge:
        raise HTTPException(status_code=503, detail="Monitoring bridge not available")
    
    try:
        export_data = bridge.export_metrics(format)
        return export_data
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to export metrics: {exc}")


@api_v1.post("/chat", response_model=ChatResponse, summary="Chat (non-streaming)", description="Send a chat request; returns the full response body.")
def v1_chat(req: ChatRequest) -> ChatResponse:
    """Non-streaming chat via new runtime."""
    if not (_new_runtime_available and new_ollama_client and NewChatMessage):
        raise HTTPException(status_code=503, detail="New runtime unavailable")
    try:
        messages = [NewChatMessage(role=m.role, content=m.content) for m in req.messages]
        resp = new_ollama_client.chat(
            messages,
            model=req.model or getattr(new_config.ollama, "model", None),
            temperature=req.temperature,
            max_tokens=req.max_tokens,
            stream=False,
        )
        return ChatResponse(content=getattr(resp, "content", ""), model=getattr(resp, "model", None))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chat failed: {exc}")


@api_v1.post("/local_chat", response_model=ChatResponse, summary="Local-only chat", description="Force local (Ollama) model usage for a chat request.")
def v1_local_chat(req: ChatRequest) -> ChatResponse:
    """Route chat request to local-only models (Ollama).

    This endpoint bypasses cloud providers and forces local model invocations.
    It uses the `MCPJarvisAgent` with `force_local=True` to ensure a local model processes the prompt.
    """
    try:
        agent = MCPJarvisAgent(enable_mcp=True)
        text = " ".join(m.content for m in req.messages)
        content = agent.chat(text, force_local=True)
        return ChatResponse(content=content, model="ollama")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Local chat failed: {exc}")


@api_v1.post("/chat/stream", summary="Chat (streaming)", description="Stream a chat response as a text/plain event stream.")
def v1_chat_stream(req: ChatRequest):
    """Streaming chat via new runtime."""
    if not (_new_runtime_available and new_ollama_client and NewChatMessage):
        raise HTTPException(status_code=503, detail="New runtime unavailable")

    def _generator():
        try:
            messages = [NewChatMessage(role=m.role, content=m.content) for m in req.messages]
            gen = new_ollama_client.chat(
                messages,
                model=req.model or getattr(new_config.ollama, "model", None),
                temperature=req.temperature,
                max_tokens=req.max_tokens,
                stream=True,
            )
            for chunk in gen:
                if chunk and getattr(chunk, "content", ""):
                    yield (chunk.content or "")
        except Exception:
            return

    return StreamingResponse(_generator(), media_type="text/plain")


# -----------------------
# v1 Feed Ingestion
# -----------------------

@api_v1.post("/feed/ingest", response_model=FeedIngestResponse, summary="Ingest feed items", description="Ingest external items into memory and/or knowledge graph.")
def v1_feed_ingest(req: FeedIngestRequest) -> FeedIngestResponse:
    ingested = 0
    errors = 0

    # Store feed in memory and knowledge graph (best effort)
    if req.items:
        for item in req.items:
            try:
                if req.persist_to_memory and new_conversation_memory is not None:
                    # Simplified: append as a system note
                    if hasattr(new_conversation_memory, "add_conversation"):
                        new_conversation_memory.add_conversation({
                            "id": item.id or "feed",
                            "messages": [{"role": "system", "content": item.content}],
                            "metadata": item.metadata or {"source": item.source or "feed"}
                        })
                if req.persist_to_knowledge and new_knowledge_graph is not None:
                    # Simplified: add node for item
                    if hasattr(new_knowledge_graph, "add_fact"):
                        new_knowledge_graph.add_fact(
                            subject=item.metadata.get("subject") if item.metadata else (item.source or "feed"),
                            predicate="mentions",
                            obj=item.content
                        )
                ingested += 1
            except Exception:
                errors += 1

    return FeedIngestResponse(ingested=ingested, errors=errors)


# -----------------------
# v1 Job Submission + Exit
# -----------------------
import uuid as _uuid
_jobs: Dict[str, Dict[str, Any]] = {}


@api_v1.post("/jobs", response_model=JobResponse, summary="Submit async job", description="Submit a chat|agent|workflow job; optionally set a webhook callback.")
async def v1_submit_job(req: JobRequest) -> JobResponse:
    job_id = str(_uuid.uuid4())
    _jobs[job_id] = {"status": "queued", "result": None, "callback": req.callback_url}

    async def _run_job():
        try:
            _jobs[job_id]["status"] = "running"
            mode = req.mode.lower()
            result: Dict[str, Any] = {"ok": True}
            if mode == "chat":
                messages = req.payload.get("messages", [])
                model = req.payload.get("model")
                temperature = req.payload.get("temperature")
                max_tokens = req.payload.get("max_tokens")
                chat_req = ChatRequest(messages=[ChatMessage(**m) for m in messages], model=model, temperature=temperature, max_tokens=max_tokens)
                chat_resp = v1_chat(chat_req)
                result = {"type": "chat", "response": chat_resp.dict()}
            elif mode == "agent":
                agent_type = req.payload.get("agent_type", "research")
                objective = req.payload.get("objective", "")
                context = req.payload.get("context", {})
                task_req = AgentTaskRequest(agent_type=agent_type, objective=objective, context=context)
                agent_result = await v1_execute_agent_task(task_req)
                result = {"type": "agent", "response": agent_result}
            elif mode == "workflow":
                wf_type = req.payload.get("workflow_type", "research")
                parameters = req.payload.get("parameters", {})
                wf_req = WorkflowTaskRequest(workflow_type=wf_type, parameters=parameters)
                wf_result = await v1_execute_workflow_task(wf_req)
                result = {"type": "workflow", "response": wf_result}
            else:
                result = {"ok": False, "error": f"Unknown mode: {mode}"}

            _jobs[job_id]["result"] = result
            _jobs[job_id]["status"] = "completed"

            # Optional callback webhook
            cb = _jobs[job_id]["callback"]
            if cb:
                try:
                    import requests as _requests
                    _requests.post(cb, json={"job_id": job_id, "status": "completed", "result": result}, timeout=10)
                except Exception:
                    pass
        except Exception as e:
            _jobs[job_id]["status"] = "failed"
            _jobs[job_id]["result"] = {"ok": False, "error": str(e)}

    asyncio.create_task(_run_job())
    return JobResponse(job_id=job_id, status="queued")


@api_v1.get("/jobs/{job_id}", response_model=JobStatusResponse, summary="Get job status", description="Poll the status and result of a submitted job.")
def v1_get_job(job_id: str) -> JobStatusResponse:
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatusResponse(job_id=job_id, status=job.get("status", "unknown"), result=job.get("result"))


# Register v1 router
app.include_router(api_v1)


if __name__ == "__main__":
    # Run the FastAPI app via Uvicorn when executed directly
    import os as _os
    import uvicorn as _uvicorn

    _host = _os.environ.get("JARVIS_BACKEND_HOST", "127.0.0.1")
    _port = int(_os.environ.get("JARVIS_BACKEND_PORT", "8000"))

    _uvicorn.run(app, host=_host, port=_port)
