from fastapi import (
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