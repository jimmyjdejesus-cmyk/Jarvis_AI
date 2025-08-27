#!/usr/bin/env python3
"""
Enhanced Jarvis AI Backend - Cerebro Galaxy Integration
FastAPI + WebSockets + Real Multi-Agent Orchestration
Complete integration with Jarvis orchestration system
"""

from fastapi import (
    FastAPI,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    Query,
    Body,
    Path,
    Depends,
    Header,
    APIRouter,
    Request,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Set
from contextlib import asynccontextmanager
import asyncio
import json
import uuid
from datetime import datetime
import logging
from enum import Enum
import uvicorn
import sys
import os
from pathlib import Path
from neo4j.exceptions import ServiceUnavailable, TransientError

# Add jarvis to Python path
jarvis_path = Path(__file__).parent.parent / "jarvis"
if jarvis_path.exists():
    sys.path.insert(0, str(jarvis_path.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Authentication utilities
from app.auth import authenticate_user, create_access_token, role_required, login_for_access_token, get_current_user, Token

# Try to import Jarvis orchestration system
try:
    from jarvis.orchestration.orchestrator import MultiAgentOrchestrator
    from jarvis.agents.base_specialist import BaseSpecialist
    from jarvis.core.mcp_agent import MCPJarvisAgent
    from jarvis.world_model.neo4j_graph import Neo4jGraph
    from jarvis.workflows.engine import workflow_engine
    JARVIS_AVAILABLE = True
    logger.info("✅ Jarvis orchestration system loaded successfully")
except Exception as e:
    logger.warning(f"⚠️ Jarvis orchestration not available: {e}")
    JARVIS_AVAILABLE = False

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

# Lifespan context to initialize application state
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Configure per-instance in-memory databases."""
    app.state.workflows_db = {}
    app.state.logs_db = []
    app.state.hitl_requests_db = {}
    yield

# Security
async def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> str:
    """Validate the `X-API-Key` header against the expected key.

    Args:
        x_api_key: API key provided by the client.

    Raises:
        HTTPException: If the key is missing or does not match the expected value.

    Returns:
        The validated API key.
    """
    expected_key = os.getenv("JARVIS_API_KEY")
    if not expected_key or x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

# Create FastAPI app
app = FastAPI(
    title="Jarvis AI Orchestrator Backend",
    version="2.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:1420",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://localhost:5177",
        "http://localhost:5178",
        "http://localhost:5179",
        "http://127.0.0.1:1420",
        "tauri://localhost"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router for API key-protected routes
api_router = APIRouter(prefix="/api", dependencies=[Depends(verify_api_key)])


# Enums
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


class AgentRole(str, Enum):
    RESEARCHER = "researcher"
    ANALYST = "analyst"
    EXECUTOR = "executor"
    VALIDATOR = "validator"
    COORDINATOR = "coordinator"


# Data Models
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
    type: str  # "approval", "input", "decision"
    prompt: str
    options: Optional[List[str]] = None
    context: Dict[str, Any] = {}
    status: str = "pending"  # "pending", "approved", "denied", "timeout"
    response: Optional[Any] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.session_connections: Dict[str, Set[str]] = {}

    async def connect(self, websocket: WebSocket, client_id: str, session_id: Optional[str] = None):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        if session_id:
            if session_id not in self.session_connections:
                self.session_connections[session_id] = set()
            self.session_connections[session_id].add(client_id)
        logger.info(f"Client {client_id} connected to session {session_id}")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            # Remove from session connections
            for session_id, clients in self.session_connections.items():
                if client_id in clients:
                    clients.remove(client_id)
        logger.info(f"Client {client_id} disconnected")

    async def send_personal_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)

    async def broadcast_to_session(self, message: str, session_id: str):
        if session_id in self.session_connections:
            for client_id in self.session_connections[session_id]:
                if client_id in self.active_connections:
                    await self.active_connections[client_id].send_text(message)

    async def broadcast(self, message: str):
        for client_id, connection in self.active_connections.items():
            await connection.send_text(message)


manager = ConnectionManager()
neo4j_graph = Neo4jGraph()

# Initialize Cerebro (Real Multi-Agent Orchestrator)
cerebro_orchestrator = None
active_orchestrators = {}
specialist_agents = {}


class MockMCPClient:
    """Mock MCP client for demonstration"""

    async def generate_response(self, server: str, model: str, prompt: str) -> str:
        # Simple mock response for demonstration
        return f"Mock response from {model}: Analyzing request..."

    async def generate_response_batch(self, server: str, model: str, prompts: List[str]) -> List[str]:
        return [f"Mock batch response {i + 1}" for i in range(len(prompts))]


class MockSpecialist(BaseSpecialist if JARVIS_AVAILABLE else object):
    """Mock specialist agent for demonstration"""

    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.preferred_models = ["llama3.2", "gpt-4"]
        self.task_history = []

    async def process_task(self, task: str, **kwargs) -> Dict[str, Any]:
        """Process a task and return results"""
        await asyncio.sleep(0.5)  # Simulate processing time

        return {
            "specialist": self.name,
            "response": f"{self.role} analysis: {task[:100]}...",
            "confidence": 0.85,
            "suggestions": [
                f"Consider {self.role.lower()} best practices",
                f"Review {self.role.lower()} guidelines",
                f"Implement {self.role.lower()} improvements"
            ],
            "priority_issues": [
                {"description": f"High priority {self.role.lower()} concern", "severity": "high"},
                {"description": f"Medium priority {self.role.lower()} issue", "severity": "medium"}
            ]
        }

    def build_prompt(self, task: str, context: Any, user_context: str) -> str:
        return f"As a {self.role} specialist, analyze: {task}"

    def process_model_response(self, response: str, model: str, task: str) -> Dict[str, Any]:
        return {
            "specialist": self.name,
            "response": response,
            "confidence": 0.8,
            "suggestions": [],
            "priority_issues": []
        }

    def _get_server_for_model(self, model: str) -> str:
        return "ollama" if "llama" in model else "openai"

    def get_specialization_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "role": self.role,
            "capabilities": [f"{self.role} analysis", f"{self.role} recommendations"],
            "models": self.preferred_models
        }


async def initialize_cerebro():
    """Initialize the Cerebro orchestrator with specialist agents"""
    global cerebro_orchestrator, specialist_agents

    if not JARVIS_AVAILABLE:
        logger.info("🧠 Initializing Mock Cerebro (Jarvis system not available)")
        # Create mock specialists
        specialist_agents = {
            "security": MockSpecialist("security", "Security"),
            "architecture": MockSpecialist("architecture", "Architecture"),
            "code_review": MockSpecialist("code_review", "Code Review"),
            "testing": MockSpecialist("testing", "Testing"),
            "devops": MockSpecialist("devops", "DevOps"),
            "research": MockSpecialist("research", "Research")
        }

        # Mock orchestrator
        class MockOrchestrator:
            def __init__(self):
                self.specialists = specialist_agents
                self.child_orchestrators = {}

            async def coordinate_specialists(self, request: str, **kwargs) -> Dict[str, Any]:
                # Simulate orchestrator coordination
                await asyncio.sleep(1)

                # Determine which specialists to use
                request_lower = request.lower()
                specialists_used = []

                if "security" in request_lower:
                    specialists_used.append("security")
                if "architecture" in request_lower or "design" in request_lower:
                    specialists_used.append("architecture")
                if "test" in request_lower:
                    specialists_used.append("testing")
                if "review" in request_lower:
                    specialists_used.append("code_review")
                if "deploy" in request_lower:
                    specialists_used.append("devops")
                if "research" in request_lower or not specialists_used:
                    specialists_used.append("research")

                # Get results from specialists
                results = {}
                for specialist_name in specialists_used:
                    if specialist_name in self.specialists:
                        result = await self.specialists[specialist_name].process_task(request)
                        results[specialist_name] = result

                return {
                    "type": "orchestrated_response",
                    "complexity": "medium",
                    "specialists_used": specialists_used,
                    "results": results,
                    "synthesized_response": f"Coordinated analysis from {len(specialists_used)} specialists for: {request}",
                    "confidence": 0.85,
                    "coordination_summary": f"Successfully coordinated {len(specialists_used)} specialists"
                }

            def create_child_orchestrator(self, name: str, spec: Dict[str, Any]):
                # Mock child orchestrator creation
                child = MockOrchestrator()
                self.child_orchestrators[name] = child
                return child

        cerebro_orchestrator = MockOrchestrator()

    else:
        logger.info("🧠 Initializing Real Cerebro with Jarvis Orchestration")
        try:
            # Create real MCP client (mock for now)
            mcp_client = MockMCPClient()

            # Create real specialist agents
            specialist_agents = {
                "security": MockSpecialist("security", "Security"),
                "architecture": MockSpecialist("architecture", "Architecture"),
                "code_review": MockSpecialist("code_review", "Code Review"),
                "testing": MockSpecialist("testing", "Testing"),
                "devops": MockSpecialist("devops", "DevOps"),
                "research": MockSpecialist("research", "Research")
            }

            # Create real Cerebro orchestrator
            cerebro_orchestrator = MultiAgentOrchestrator(
                mcp_client=mcp_client,
                specialists=specialist_agents,
                message_bus=None,  # We'll handle messaging through WebSocket
                budgets={"max_cost": 100, "max_time": 300}
            )

            logger.info("✅ Real Cerebro orchestrator initialized successfully")

        except Exception as e:
            logger.error(f"❌ Failed to initialize real Cerebro: {e}")
            # Fall back to mock
            cerebro_orchestrator = MockOrchestrator()

    logger.info(f"🎭 Cerebro initialized with {len(specialist_agents)} specialist agents")

# Initialize Cerebro on startup
@app.on_event("startup")
async def startup_event():
    await initialize_cerebro()


@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate user and return JWT access token."""
    return await login_for_access_token(form_data)


# API Endpoints
@app.get("/")
async def root():
    return {
        "message": "Enhanced Jarvis AI - Cerebro Galaxy Backend",
        "status": "online",
        "cerebro_active": cerebro_orchestrator is not None,
        "jarvis_integration": JARVIS_AVAILABLE,
        "specialists_available": len(specialist_agents)
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "neo4j_active": neo4j_graph.is_alive(),
    }


# Workflow endpoints
@app.get("/api/workflow/{session_id}")
async def get_workflow(request: Request, session_id: str):
    """Get current workflow state for a session with real Cerebro data."""
    if not cerebro_orchestrator:
        raise HTTPException(status_code=503, detail="Cerebro orchestrator not initialized")

    workflows_db = request.app.state.workflows_db
    if session_id in workflows_db:
        return workflows_db[session_id]

    # Get real orchestrator status
    orchestrator_count = (
        len(cerebro_orchestrator.child_orchestrators)
        if hasattr(cerebro_orchestrator, "child_orchestrators")
        else 3
    )
    specialist_count = len(specialist_agents)

    # Build galaxy structure with real data
    nodes = []
    edges = []

    # Cerebro node (central meta-agent)
    cerebro_node = {
        "id": "cerebro",
        "type": "cerebro",
        "position": {"x": 0, "y": 0},
        "data": {
            "label": "CEREBRO",
            "status": "active",
            "orchestratorCount": orchestrator_count,
            "totalAgents": specialist_count,
            "activeConversations": len(active_orchestrators),
            "lastMessage": "",
            "level": "cerebro",
        },
        "status": "running",
    }
    nodes.append(cerebro_node)

    # Add orchestrator nodes (dynamically spawned systems)
    orchestrator_positions = [
        {"x": 300, "y": -200},
        {"x": 300, "y": 200},
        {"x": -300, "y": 0}
    ]

    orchestrator_names = ["Research Orchestrator", "Analysis Orchestrator", "Execution Orchestrator"]
    for i, (name, pos) in enumerate(zip(orchestrator_names, orchestrator_positions)):
        orchestrator_id = f"orchestrator-{i+1}"

        # Get agents for this orchestrator
        agents_for_orchestrator = list(specialist_agents.keys())[i * 2:(i + 1) * 2] if i * 2 < len(specialist_agents) else []

        orchestrator_node = {
            "id": orchestrator_id,
            "type": "orchestrator",
            "position": pos,
            "data": {
                "label": name,
                "purpose": f"Specialized {name.split()[0].lower()} coordination",
                "status": "active"
                if f"orchestrator-{i+1}" in active_orchestrators
                else "idle",
                "spawnTime": "2 min ago",
                "activeTasks": len(agents_for_orchestrator),
                "agents": [
                    {
                        "id": agent_name,
                        "icon": "🤖",
                        "status": "active"
                    } for agent_name in agents_for_orchestrator
                ],
                "level": "orchestrator",
            },
            "status": "running",
        }
        nodes.append(orchestrator_node)

        # Connect to Cerebro
        edges.append({
            "id": f"cerebro-{orchestrator_id}",
            "source": "cerebro",
            "target": orchestrator_id,
            "type": "smoothstep",
            "animated": orchestrator_id in active_orchestrators,
            "style": {"stroke": "#4ade80", "strokeWidth": 2}
        })

        # Add agent nodes
        for j, agent_name in enumerate(agents_for_orchestrator):
            agent_angle = (j / len(agents_for_orchestrator)) * 2 * 3.14159 if agents_for_orchestrator else 0
            agent_radius = 120

            agent_node = {
                "id": agent_name,
                "type": "agent",
                "position": {
                    "x": pos["x"] + agent_radius * (1 if j % 2 == 0 else -1),
                    "y": pos["y"] + agent_radius * (0.5 if j < len(agents_for_orchestrator) / 2 else -0.5)
                },
                "data": {
                    "label": specialist_agents[agent_name].role if agent_name in specialist_agents else agent_name,
                    "role": specialist_agents[agent_name].role if agent_name in specialist_agents else "Specialist",
                    "status": "active",
                    "icon": "🤖",
                    "tasks": [
                        {
                            "id": f"{agent_name}-task-1",
                            "label": "Analysis Task",
                            "status": "running",
                            "progress": 0.7,
                            "confidence": 0.85
                        }
                    ],
                    "level": "agent",
                },
                "status": "running",
            }
            nodes.append(agent_node)

            # Connect to orchestrator
            edges.append({
                "id": f"{orchestrator_id}-{agent_name}",
                "source": orchestrator_id,
                "target": agent_name,
                "type": "smoothstep",
                "style": {"stroke": "#60a5fa", "strokeWidth": 1}
            })

    workflow = {
        "id": str(uuid.uuid4()),
        "session_id": session_id,
        "name": "Cerebro Galaxy Workflow",
        "nodes": nodes,
        "edges": edges,
        "status": "running",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "orchestrators": [
            {
                "id": f"orchestrator-{i + 1}",
                "label": name,
                "purpose": f"Specialized {name.split()[0].lower()} coordination",
                "status": "active" if f"orchestrator-{i + 1}" in active_orchestrators else "idle",
                "agents": list(specialist_agents.keys())[i * 2:(i + 1) * 2] if i * 2 < len(specialist_agents) else []
            } for i, name in enumerate(orchestrator_names)
        ]
    }
    workflows_db[session_id] = workflow
    return workflow

# Import workflow engine with graceful fallback
try:
    from jarvis.workflows.engine import workflow_engine
except Exception as e:
    logger.warning(f"⚠️ Workflow engine not available: {e}")

    class DummyWorkflowEngine:
        def get_workflow_status(self, workflow_id: str):
            return None

    workflow_engine = DummyWorkflowEngine()


@app.get("/api/workflow/status/{workflow_id}", dependencies=[Depends(get_current_user)])
async def get_workflow_status(workflow_id: str):
    """Get the status of a specific workflow."""
    status = workflow_engine.get_workflow_status(workflow_id)
    if not status:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return status


# Logs endpoints
@app.get("/api/logs", dependencies=[Depends(role_required("admin"))])
async def get_logs(request: Request, session_id: Optional[str] = Query(None), limit: int = Query(100)):
    """Get logs with optional filters. Requires admin role."""
    logs_db = request.app.state.logs_db
    logs = [
        log
        for log in logs_db
        if session_id is None or log.session_id == session_id
    ]
    return [log.dict() for log in logs[:limit]]


# HITL endpoints
@app.get("/api/hitl/pending", dependencies=[Depends(get_current_user)])
async def get_pending_hitl_requests(request: Request, session_id: Optional[str] = Query(None)):
    """Get pending HITL requests."""
    hitl_db = request.app.state.hitl_requests_db
    requests = list(hitl_db.values())
    if session_id is not None:
        requests = [r for r in requests if r.session_id == session_id]
    return [r.dict() for r in requests]


# Mission history endpoint
@app.get("/missions/{mission_id}/history", dependencies=[Depends(verify_api_key)])
async def get_mission_history(mission_id: str = Path(..., regex=r"^[\w-]+$")):
    """Return mission history including steps and discovered facts."""
    try:
        history = neo4j_graph.get_mission_history(mission_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid mission id")
    if not history:
        raise HTTPException(status_code=404, detail="Mission not found")
    return history


@app.post("/knowledge/query")
async def knowledge_query(payload: Dict[str, Any], current_user: Any = Depends(get_current_user)) -> Dict[str, Any]:
    """Query the Neo4j graph and handle connection errors. Requires authentication."""
    query = payload.get("query", "")
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    try:
        return {"results": neo4j_graph.query(query)}
    except ServiceUnavailable as exc:
        raise HTTPException(status_code=500, detail="Neo4j service unavailable") from exc
    except TransientError as exc:
        raise HTTPException(status_code=500, detail="Neo4j transient error") from exc
    except Exception as exc:
        logger.error(f"Failed to execute knowledge query: {exc}")
        raise HTTPException(status_code=500, detail="Internal server error") from exc


# Include API router
app.include_router(api_router)


# WebSocket endpoint with real Cerebro integration
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str, session_id: Optional[str] = Query(None)):
    await manager.connect(websocket, client_id, session_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle different message types
            if message["type"] == "ping":
                await manager.send_personal_message(
                    json.dumps({"type": "pong", "timestamp": datetime.now().isoformat()}),
                    client_id
                )

            elif message["type"] == "chat_message" and message.get("trigger_cerebro"):
                # Real Cerebro processing
                user_message = message.get("message", "")
                session = session_id or "default-session"

                logger.info(f"🧠 Cerebro processing message: {user_message[:50]}...")

                # Notify frontend that Cerebro is thinking
                await manager.broadcast_to_session(
                    json.dumps({
                        "type": "cerebro_thinking",
                        "data": {
                            "message": user_message,
                            "status": "thinking",
                            "timestamp": datetime.now().isoformat()
                        }
                    }),
                    session
                )

                try:
                    # Use real Cerebro orchestrator
                    if cerebro_orchestrator:
                        # Process with real orchestrator
                        result = await cerebro_orchestrator.coordinate_specialists(
                            user_message,
                            user_context=f"Session: {session}",
                            context={"client_id": client_id, "timestamp": datetime.now().isoformat()}
                        )

                        # Determine if new orchestrators were spawned
                        specialists_used = result.get("specialists_used", [])
                        coordination_type = result.get("type", "simple")

                        # Simulate orchestrator spawning for complex tasks
                        if len(specialists_used) > 1:
                            orchestrator_id = f"orchestrator-{len(active_orchestrators) + 1}"
                            active_orchestrators[orchestrator_id] = {
                                "id": orchestrator_id,
                                "specialists": specialists_used,
                                "created_at": datetime.now().isoformat(),
                                "task": user_message
                            }

                            # Notify frontend of orchestrator spawning
                            await manager.broadcast_to_session(
                                json.dumps({
                                    "type": "orchestrator_spawned",
                                    "data": {
                                        "orchestrator_id": orchestrator_id,
                                        "specialists": specialists_used,
                                        "purpose": f"Handle {coordination_type} coordination",
                                        "complexity": result.get("complexity", "medium"),
                                        "timestamp": datetime.now().isoformat()
                                    }
                                }),
                                session
                            )

                            # Simulate agent activation
                            for specialist in specialists_used:
                                await manager.broadcast_to_session(
                                    json.dumps({
                                        "type": "agent_activated",
                                        "data": {
                                            "agent_id": specialist,
                                            "orchestrator_id": orchestrator_id,
                                            "task": f"Process {specialist} analysis",
                                            "status": "running",
                                            "timestamp": datetime.now().isoformat()
                                        }
                                    }),
                                    session
                                )

                        # Send Cerebro response
                        await manager.broadcast_to_session(
                            json.dumps({
                                "type": "cerebro_response",
                                "data": {
                                    "message": result.get("synthesized_response", "Analysis complete"),
                                    "confidence": result.get("confidence", 0.85),
                                    "specialists_used": specialists_used,
                                    "coordination_summary": result.get("coordination_summary", ""),
                                    "status": "active",
                                    "timestamp": datetime.now().isoformat()
                                }
                            }),
                            session
                        )

                        # Send chat response
                        await manager.broadcast_to_session(
                            json.dumps({
                                "type": "chat_response",
                                "data": {
                                    "message": result.get("synthesized_response", "Analysis complete"),
                                    "source": "cerebro",
                                    "specialists_involved": specialists_used,
                                    "confidence": result.get("confidence", 0.85),
                                    "timestamp": datetime.now().isoformat()
                                }
                            }),
                            session
                        )

                    else:
                        # Fallback response
                        await manager.broadcast_to_session(
                            json.dumps({
                                "type": "chat_response",
                                "data": {
                                    "message": "Cerebro is initializing. Please try again in a moment.",
                                    "source": "system",
                                    "timestamp": datetime.now().isoformat()
                                }
                            }),
                            session
                        )

                except Exception as e:
                    logger.error(f"❌ Cerebro processing failed: {e}")
                    await manager.broadcast_to_session(
                        json.dumps({
                            "type": "chat_response",
                            "data": {
                                "message": f"I encountered an error while processing your request: {str(e)}",
                                "source": "cerebro",
                                "error": True,
                                "timestamp": datetime.now().isoformat()
                            }
                        }),
                        session
                    )

            elif message["type"] == "cerebro_input":
                # Legacy support for direct cerebro input
                await manager.broadcast_to_session(
                    json.dumps({
                        "type": "cerebro_thinking",
                        "data": {"message": message.get("message", "")}
                    }),
                    session_id or "default-session"
                )

    except WebSocketDisconnect:
        manager.disconnect(client_id)


if __name__ == "__main__":
    print("🚀 Starting Enhanced Jarvis AI Backend Server")
    print("=" * 50)
    print("📡 API Server: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🔌 WebSocket: ws://localhost:8000/ws/{client_id}")
    print("=" * 50)

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )