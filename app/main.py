import logging

from fastapi import (
    FastAPI,
    HTTPException,
)
from fastapi.middleware.cors import CORSMiddleware


# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Optional Jarvis imports (guarded to keep imports clean in minimal contexts)
try:
    from jarvis.orchestration.orchestrator import MultiAgentOrchestrator  # noqa: F401
    from jarvis.workflows.engine import workflow_engine  # noqa: F401
    JARVIS_AVAILABLE = True
except Exception as e:  # pragma: no cover - optional in tests
    logger.warning(
        "Jarvis optional packages not available; running in minimal mode: %s",
        e,
    )
    JARVIS_AVAILABLE = False


# FastAPI app instance
app = FastAPI(title="J.A.R.V.I.S. API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "jarvis": JARVIS_AVAILABLE}

