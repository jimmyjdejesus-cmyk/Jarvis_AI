#!/usr/bin/env python3
"""
Enhanced Jarvis AI Backend - Cerebro Galaxy Integration
FastAPI + WebSockets + Real Multi-Agent Orchestration
Complete integration with Jarvis orchestration system
"""

# Standard library imports
import asyncio
import json
import logging
import os
import sys
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Third-party imports
import uvicorn
from fastapi import (
    APIRouter,
    Body,
    Depends,
    FastAPI,
    Header,
    HTTPException,
    Path as FPath,
    Query,
    Request,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from neo4j.exceptions import ServiceUnavailable, TransientError
from pydantic import BaseModel, Field

# --- Add Jarvis to Python Path ---
# This allows for importing the local jarvis module
try:
    _current_file = Path(__file__)
except NameError:  # pragma: no cover - execution via `exec` lacks __file__
    _current_file = Path("jarvis/ecosystem/meta_intelligence.py")
jarvis_path = _current_file.parent.parent / "jarvis"
if jarvis_path.exists():
    sys.path.insert(0, str(jarvis_path.parent))

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Application-specific Imports ---
# Authentication utilities
from app.auth import (Token, authenticate_user, create_access_token,
                      get_current_user, login_for_access_token, role_required)

# Attempt to import the full Jarvis orchestration system
# If it fails, create mock objects to allow the server to run for frontend development
try:
    from jarvis.agents.base_specialist import BaseSpecialist
    from jarvis.agents.curiosity_agent import CuriosityAgent
    from jarvis.agents.mission_planner import MissionPlanner
    from jarvis.core.mcp_agent import MCPJarvisAgent
    from jarvis.orchestration.mission import Mission, MissionDAG
    from jarvis.orchestration.orchestrator import MultiAgentOrchestrator
    from jarvis.world_model.hypergraph import HierarchicalHypergraph
    from jarvis.world_model.neo4j_graph import Neo4jGraph
    from jarvis.workflows.engine import WorkflowStatus, from_mission_dag, workflow_engine
    JARVIS_AVAILABLE = True
    logger.info("✅ Jarvis orchestration system loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ Jarvis orchestration not available, using mock objects: {e}")
    JARVIS_AVAILABLE = False

    # --- Mock Jarvis Components ---
    class Neo4jGraph:
        def __init__(self, *args, **kwargs):
            pass
        def is_alive(self):
            return False
        def get_mission_history(self, mission_id):
            return None
        def query(self, query):
            raise ServiceUnavailable("Mock Neo4j is not available")

    class workflow_engine:
        def get_workflow_status(self, workflow_id):
            return None

    class BaseSpecialist:
        pass # Base class for mock specialist

# --- Executive Agent Implementation ---
class ExecutiveAgent:
    """High-level orchestrator that records mission progress in Neo4j."""

    def __init__(self, agent_id: str) -> None:
        self.agent_id = agent_id
        self.mission_planner = MissionPlanner()
        self.neo4j_graph: Optional[Neo4jGraph] = None

    def manage_directive(
        self, directive: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Plan a directive into tasks and a mission graph.

        This lightweight implementation is primarily a stub and is patched in
        tests. It returns a structure compatible with
        :class:`MissionPlanner` outputs.
        """

        tasks = self.mission_planner.plan(directive)
        graph = self.mission_planner.to_graph(tasks)
        return {"success": True, "tasks": tasks, "graph": graph}

    async def execute_mission(
        self, objective: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a mission and update the world model.

        A :class:`Neo4jGraph` is instantiated for the mission and closed when
        execution completes. After each mission step the graph is updated with
        new nodes and edges describing progress and discovered facts.
        """

        plan = self.manage_directive(objective, context)
        if not plan.get("success"):
            message = plan.get("critique", {}).get("message", "")
            return {
                "success": False,
                "error": f"Mission planning failed: {message}",
            }

        dag = MissionDAG.from_dict(plan["graph"])
        workflow = from_mission_dag(dag)

        self.neo4j_graph = Neo4jGraph()
        try:
            completed = await workflow_engine.execute_workflow(workflow)

            mission = Mission(
                id=dag.mission_id,
                title=objective,
                goal=objective,
                inputs=context,
                risk_level=context.get("risk_level", "low"),
                dag=dag,
            )

            for step_id, step_result in completed.context.results.items():
                step_info = {
                    "step_id": step_id,
                    "success": True,
                    "facts": getattr(step_result, "facts", []),
                    "relationships": getattr(step_result, "relationships", []),
                }
                try:
                    self._update_world_model(mission, [step_info])
                except Exception as exc:  # pragma: no cover - best effort
                    logger.warning(
                        "World model update failed for step %s: %s", step_id, exc
                    )

            status = (
                completed.status.value
                if isinstance(completed.status, Enum)
                else str(completed.status)
            )
            return {
                "success": True,
                "results": {
                    "workflow_id": completed.workflow_id,
                    "status": status.lower(),
                },
            }
        finally:
            if self.neo4j_graph:
                self.neo4j_graph.close()

    def _update_world_model(
        self, mission: Mission, results: List[Dict[str, Any]]
    ) -> None:
        """Persist mission and step data to the Neo4j graph."""

        if not self.neo4j_graph:
            return

        # Mission context
        self.neo4j_graph.add_node(
            mission.id,
            "mission",
            {"goal": mission.goal, "rationale": mission.dag.rationale},
        )

        for step_id, node in mission.dag.nodes.items():
            self.neo4j_graph.add_node(
                step_id,
                "step",
                {"capability": node.capability, "team_scope": node.team_scope},
            )
            self.neo4j_graph.add_edge(mission.id, step_id, "HAS_STEP")

        for result in results:
            step_id = result["step_id"]
            status = "COMPLETED" if result.get("success") else "FAILED"
            self.neo4j_graph.add_node(step_id, "step", {"status": status})
            self.neo4j_graph.add_edge(mission.id, step_id, status)

            for fact in result.get("facts", []):
                self.neo4j_graph.add_node(
                    fact["id"], fact.get("type", "fact"), fact.get("attributes")
                )
                self.neo4j_graph.add_edge(step_id, fact["id"], "DISCOVERED")

            for rel in result.get("relationships", []):
                self.neo4j_graph.add_edge(rel["source"], rel["target"], rel["type"])


__all__ = ["ExecutiveAgent"]

# --- Security and API Key Verification ---
async def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> str:
    """
    Validates the `X-API-Key` header against the expected key from environment variables.
    """
    expected_key = os.getenv("JARVIS_API_KEY")
    if not expected_key or x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

# --- FastAPI Application Setup ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown events.
    Initializes state and cleans up resources.
    """
    # --- In-memory Storage Initialization ---
    # NOTE: This is NOT suitable for production. Data will be lost on restart.
    # For production, replace with a persistent solution like Redis for caching
    # and a database (e.g., PostgreSQL, MongoDB) for permanent storage.
    app.state.workflows_db = {}
    app.state.logs_db = []
    app.state.hitl_requests_db = {}
    app.state.active_orchestrators = {}

    # Initialize Cerebro on startup
    await initialize_cerebro()
    yield
    # Cleanup logic can go here if needed

app = FastAPI(
    title="Jarvis AI Orchestrator Backend",
    version="2.0.0",
    lifespan=lifespan
)

# --- CORS Middleware Configuration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:1420", "http://127.0.0.1:1420", "tauri://localhost",
        "http://localhost:5173", "http://localhost:5174", "http://localhost:5175",
        "http://localhost:5176", "http://localhost:5177", "http://localhost:5178",
        "http://localhost:5179",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Router for Key-Protected Routes ---
api_router = APIRouter(prefix="/api", dependencies=[Depends(verify_api_key)])

# --- Enums and Data Models ---

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    DEAD_END = "dead_end"
    HITL_REQUIRED = "hitl_required"

class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class WorkflowNode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str
    position: Dict[str, float]
    data: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    reasoning: Optional[str] = None
    tool_outputs: Optional[List[Dict[str, Any]]] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class WorkflowEdge(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: str
    target: str
    type: str = "default"
    animated: bool = False
    label: Optional[str] = None

class Workflow(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    name: str
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]
    status: TaskStatus = TaskStatus.PENDING
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = {}

class LogEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    agent_id: Optional[str] = None
    level: LogLevel
    message: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = {}

class HITLRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str
    session_id: str
    type: str
    prompt: str
    options: Optional[List[str]] = None
    context: Dict[str, Any] = {}
    status: str = "pending"
    response: Optional[Any] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class CypherQuery(BaseModel):
    """Pydantic model for receiving Cypher queries."""
    query: str

# --- WebSocket Connection Manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.session_connections: Dict[str, Set[str]] = {}

    async def connect(self, websocket: WebSocket, client_id: str, session_id: Optional[str] = None):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        if session_id:
            self.session_connections.setdefault(session_id, set()).add(client_id)
        logger.info(f"Client {client_id} connected to session {session_id}")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            for clients in self.session_connections.values():
                clients.discard(client_id)
        logger.info(f"Client {client_id} disconnected")

    async def send_personal_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)

    async def broadcast_to_session(self, message: str, session_id: str):
        if session_id in self.session_connections:
            clients_in_session = list(self.session_connections[session_id])
            for client_id in clients_in_session:
                if client_id in self.active_connections:
                    await self.active_connections[client_id].send_text(message)

manager = ConnectionManager()
neo4j_graph = Neo4jGraph()

# --- Cerebro (Multi-Agent Orchestrator) Initialization ---
cerebro_orchestrator = None
specialist_agents = {}

class MockMCPClient:
    """Mock MCP client for demonstration when Jarvis is not available."""
    async def generate_response(self, server: str, model: str, prompt: str) -> str:
        return f"Mock response from {model}: Analyzing request..."
    async def generate_response_batch(self, server: str, model: str, prompts: List[str]) -> List[str]:
        return [f"Mock batch response {i + 1}" for i in range(len(prompts))]

class MockSpecialist(BaseSpecialist):
    """Mock specialist agent for demonstration."""
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.preferred_models = ["llama3.2", "gpt-4"]
        self.task_history = []

    async def process_task(self, task: str, **kwargs) -> Dict[str, Any]:
        await asyncio.sleep(0.5)
        return {
            "specialist": self.name,
            "response": f"{self.role} analysis: {task[:100]}...",
            "confidence": 0.85,
            "suggestions": [f"Consider {self.role.lower()} best practices"],
            "priority_issues": [{"description": f"High priority {self.role.lower()} concern", "severity": "high"}]
        }

    def build_prompt(self, task: str, context: Any, user_context: str) -> str:
        return f"As a {self.role} specialist, analyze: {task}"

    def process_model_response(self, response: str, model: str, task: str) -> Dict[str, Any]:
        return {"specialist": self.name, "response": response, "confidence": 0.8}

    def get_specialization_info(self) -> Dict[str, Any]:
        return {"name": self.name, "role": self.role, "models": self.preferred_models}


async def initialize_cerebro():
    """Initializes the Cerebro orchestrator with specialist agents."""
    global cerebro_orchestrator, specialist_agents

    specialist_agents = {
        "security": MockSpecialist("security", "Security"),
        "architecture": MockSpecialist("architecture", "Architecture"),
        "code_review": MockSpecialist("code_review", "Code Review"),
        "testing": MockSpecialist("testing", "Testing"),
        "devops": MockSpecialist("devops", "DevOps"),
        "research": MockSpecialist("research", "Research")
    }

    if JARVIS_AVAILABLE:
        logger.info("🧠 Initializing Real Cerebro with Jarvis Orchestration")
        try:
            mcp_client = MockMCPClient() # Replace with real client when available
            cerebro_orchestrator = MultiAgentOrchestrator(
                mcp_client=mcp_client,
                specialists=specialist_agents,
                message_bus=None,
                budgets={"max_cost": 100, "max_time": 300}
            )
            logger.info("✅ Real Cerebro orchestrator initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize real Cerebro: {e}. Falling back to mock.")
            JARVIS_AVAILABLE = False # Downgrade to mock
    
    if not JARVIS_AVAILABLE:
        logger.info("🧠 Initializing Mock Cerebro (Jarvis system not available)")
        class MockOrchestrator:
            def __init__(self):
                self.specialists = specialist_agents
            async def coordinate_specialists(self, request: str, **kwargs) -> Dict[str, Any]:
                await asyncio.sleep(1)
                request_lower = request.lower()
                specialists_used = [name for name, agent in self.specialists.items() if agent.role.lower() in request_lower]
                if not specialists_used:
                    specialists_used.append("research")
                
                results = {name: await self.specialists[name].process_task(request) for name in specialists_used}
                return {
                    "type": "orchestrated_response", "specialists_used": specialists_used,
                    "results": results, "synthesized_response": f"Coordinated analysis for: {request}",
                    "confidence": 0.85, "coordination_summary": f"Coordinated {len(specialists_used)} specialists"
                }
        cerebro_orchestrator = MockOrchestrator()

    logger.info(f"🎭 Cerebro initialized with {len(specialist_agents)} specialist agents")

# --- API Endpoints ---

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticates a user and returns a JWT access token."""
    return await login_for_access_token(form_data)

@app.get("/")
async def root():
    """Root endpoint providing basic status information."""
    return {
        "message": "Enhanced Jarvis AI - Cerebro Galaxy Backend",
        "status": "online",
        "cerebro_active": cerebro_orchestrator is not None,
        "jarvis_integration": JARVIS_AVAILABLE,
        "specialists_available": len(specialist_agents)
    }

@app.get("/health")
async def health_check():
    """Provides a health check of the service and its dependencies."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "neo4j_active": neo4j_graph.is_alive() if neo4j_graph else False,
    }

# --- Workflow Endpoints ---
@api_router.get("/workflow/{session_id}", response_model=Workflow)
async def get_workflow(request: Request, session_id: str):
    """Retrieves the current workflow state for a given session."""
    if session_id not in request.app.state.workflows_db:
        raise HTTPException(status_code=404, detail="Workflow for this session not found. Create one via POST.")
    return request.app.state.workflows_db[session_id]

@api_router.post("/workflow/{session_id}", response_model=Workflow)
async def create_or_update_workflow(request: Request, session_id: str):
    """
    Creates or updates the visual workflow for a session.
    NOTE: This currently generates a static, hardcoded graph for visualization.
    In a real system, this should query the orchestrator's state.
    """
    # This is placeholder logic to generate a cool-looking graph.
    # A real implementation would dynamically build this from the orchestrator's state.
    nodes, edges = [], []
    active_orchestrators = request.app.state.active_orchestrators

    # Central Cerebro Node
    nodes.append({
        "id": "cerebro", "type": "cerebro", "position": {"x": 0, "y": 0},
        "data": {"label": "CEREBRO", "status": "active", "level": "cerebro"}, "status": "running"
    })

    # Orchestrator and Agent Nodes
    orchestrator_configs = [
        {"name": "Research", "pos": {"x": 300, "y": -200}},
        {"name": "Analysis", "pos": {"x": 300, "y": 200}},
        {"name": "Execution", "pos": {"x": -300, "y": 0}}
    ]
    agent_list = list(specialist_agents.keys())
    
    for i, config in enumerate(orchestrator_configs):
        orch_id = f"orchestrator-{i+1}"
        agents_for_orch = agent_list[i*2:(i+1)*2]
        
        nodes.append({
            "id": orch_id, "type": "orchestrator", "position": config["pos"],
            "data": {"label": f"{config['name']} Orchestrator", "status": "active" if orch_id in active_orchestrators else "idle", "level": "orchestrator"},
            "status": "running"
        })
        edges.append({"id": f"cerebro-{orch_id}", "source": "cerebro", "target": orch_id, "type": "smoothstep", "animated": orch_id in active_orchestrators})

        for j, agent_name in enumerate(agents_for_orch):
            agent_pos = {"x": config["pos"]["x"] + 150 * (1 if j % 2 == 0 else -1), "y": config["pos"]["y"] + 80 * (1 if j < 1 else -1)}
            nodes.append({
                "id": agent_name, "type": "agent", "position": agent_pos,
                "data": {"label": specialist_agents[agent_name].role, "status": "active", "level": "agent"},
                "status": "running"
            })
            edges.append({"id": f"{orch_id}-{agent_name}", "source": orch_id, "target": agent_name, "type": "smoothstep"})

    workflow = Workflow(
        session_id=session_id, name="Cerebro Galaxy Workflow",
        nodes=nodes, edges=edges, status=TaskStatus.RUNNING
    )
    request.app.state.workflows_db[session_id] = workflow
    return workflow


@api_router.get("/workflow/status/{workflow_id}")
async def get_workflow_status(workflow_id: str, current_user: Any = Depends(get_current_user)):
    """Gets the status of a specific workflow from the Jarvis engine."""
    status = workflow_engine.get_workflow_status(workflow_id)
    if not status:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return status

# --- Logs and Graph Endpoints ---
@api_router.get("/logs")
async def get_logs(request: Request, session_id: Optional[str] = Query(None), limit: int = Query(100), current_user: Any = Depends(role_required("admin"))):
    """Gets logs with optional filters. Requires admin role."""
    logs = [log for log in request.app.state.logs_db if session_id is None or log.session_id == session_id]
    return [log.dict() for log in logs[:limit]]

@api_router.post("/graph/cypher")
async def run_cypher_query(query: CypherQuery, current_user: Any = Depends(get_current_user)) -> Dict[str, Any]:
    """Executes a read-only Cypher query against the Neo4j graph."""
    if not neo4j_graph or not neo4j_graph.is_alive():
        raise HTTPException(status_code=503, detail="Neo4j graph unavailable")
    try:
        # Basic validation to prevent write operations
        if any(keyword in query.query.upper() for keyword in ["CREATE", "SET", "DELETE", "REMOVE", "MERGE"]):
            raise ValueError("Write operations are not allowed in this query endpoint.")
        results = neo4j_graph.query(query.query)
        return {"results": results}
    except (ValueError, SyntaxError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except (ServiceUnavailable, TransientError) as exc:
        raise HTTPException(status_code=503, detail=f"Neo4j service error: {exc}")
    except Exception as exc:
        logger.error(f"Failed to execute Cypher query: {exc}")
        raise HTTPException(status_code=500, detail="Internal server error during query execution.")

@api_router.get("/missions/{mission_id}/history")
async def get_mission_history(mission_id: str = FPath(..., pattern=r"^[\w-]+$")):
    """Returns mission history including steps and discovered facts."""
    try:
        history = neo4j_graph.get_mission_history(mission_id)
        if not history:
            raise HTTPException(status_code=404, detail="Mission not found")
        return history
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid mission ID format")


# --- HITL (Human-in-the-Loop) Endpoints ---
@api_router.get("/hitl/pending")
async def get_pending_hitl_requests(request: Request, session_id: Optional[str] = Query(None), current_user: Any = Depends(get_current_user)):
    """Gets pending HITL requests."""
    requests_list = [r for r in request.app.state.hitl_requests_db.values() if r.status == "pending"]
    if session_id:
        requests_list = [r for r in requests_list if r.session_id == session_id]
    return [r.dict() for r in requests_list]

# Include the API router in the main app
app.include_router(api_router)

# --- WebSocket Endpoint ---
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str, session_id: Optional[str] = Query(None)):
    """Handles real-time communication with clients via WebSockets."""
    await manager.connect(websocket, client_id, session_id)
    session = session_id or "default-session"
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            message_type = message.get("type")

            if message_type == "ping":
                await manager.send_personal_message(json.dumps({"type": "pong"}), client_id)

            elif message_type == "chat_message" and message.get("trigger_cerebro"):
                user_message = message.get("message", "")
                logger.info(f"🧠 Cerebro processing message: '{user_message[:50]}...' in session {session}")
                
                await manager.broadcast_to_session(json.dumps({"type": "cerebro_thinking"}), session)

                try:
                    if not cerebro_orchestrator:
                        raise RuntimeError("Cerebro orchestrator is not initialized.")

                    result = await cerebro_orchestrator.coordinate_specialists(
                        user_message,
                        user_context=f"Session: {session}",
                        context={"client_id": client_id}
                    )
                    
                    # Update active orchestrators for visualization
                    specialists_used = result.get("specialists_used", [])
                    if len(specialists_used) > 1:
                        # This logic is for visualization purposes
                        orch_id = f"orchestrator-{(len(websocket.app.state.active_orchestrators) % 3) + 1}"
                        websocket.app.state.active_orchestrators[orch_id] = {"task": user_message}
                        await manager.broadcast_to_session(json.dumps({"type": "orchestrator_spawned", "data": {"orchestrator_id": orch_id}}), session)

                    # Send final response
                    await manager.broadcast_to_session(json.dumps({
                        "type": "chat_response",
                        "data": {
                            "message": result.get("synthesized_response", "Analysis complete."),
                            "source": "cerebro",
                            "specialists_involved": specialists_used,
                            "confidence": result.get("confidence", 0.85),
                            "timestamp": datetime.now().isoformat()
                        }
                    }), session)

                except Exception as e:
                    logger.error(f"❌ Cerebro processing failed: {e}", exc_info=True)
                    await manager.broadcast_to_session(json.dumps({
                        "type": "chat_response",
                        "data": {
                            "message": f"An error occurred: {e}",
                            "source": "cerebro", "error": True,
                            "timestamp": datetime.now().isoformat()
                        }
                    }), session)

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"An unexpected error occurred in WebSocket: {e}", exc_info=True)
        manager.disconnect(client_id)

# --- Main Execution ---
if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Starting Enhanced Jarvis AI Backend Server")
    print(f"🔗 API Docs: http://localhost:8000/docs")
    print(f"🔌 WebSocket: ws://localhost:8000/ws/{{client_id}}")
    print("=" * 50)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
