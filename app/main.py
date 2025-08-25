import socketio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import List, Dict, Any

from jarvis.orchestration.mission import load_mission

# Create a FastAPI app instance
app = FastAPI()

# Create a Socket.IO asynchronous server instance
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins="*")

# Wrap the Socket.IO server in a Socket.IO application
socket_app = socketio.ASGIApp(sio)

# Add CORS middleware to allow cross-origin requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


def broadcast_workflow_update(update: Dict[str, Any]) -> None:
    """Background task to emit workflow updates over Socket.IO."""
    sio.start_background_task(sio.emit, "workflow:update", update)

@app.get("/")
async def read_root():
    """
    Root endpoint for the backend.
    Provides a simple response to indicate the server is running.
    """
    return {"message": "J.A.R.V.I.S. Backend is running."}

# API Endpoints for UI Panes

@app.get("/api/workflow")
async def get_workflow_data() -> Dict[str, List[Dict[str, Any]]]:
    """
    Provides data for the workflow visualization pane.
    NOTE: This endpoint is not yet implemented and will be connected
    to the core J.A.R.V.I.S. orchestrator in a future update.
    """
    raise HTTPException(
        status_code=501,
        detail="Workflow endpoint is not yet implemented."
    )


@app.get("/api/workflow/{mission_id}")
async def get_mission_workflow(mission_id: str) -> Dict[str, Any]:
    """Serve the persisted DAG for the given mission."""
    try:
        mission = load_mission(mission_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="mission not found")
    return mission.dag.to_dict()


@app.get("/api/logs")
async def get_agent_logs() -> str:
    """
    Reads and returns the content of the agent.md log file.
    This provides real-time access to the agent's operation log for the UI.
    """
    try:
        # DEV-COMMENT: It's important to handle the case where the file might not exist,
        # although our scaffolding process should have created it.
        with open("agent.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        # DEV-COMMENT: If the file is not found, we raise an HTTP 404 exception.
        # This provides a clear error message to the frontend.
        raise HTTPException(status_code=404, detail="agent.md file not found.")
    except Exception as e:
        # DEV-COMMENT: Catching other potential exceptions (e.g., permissions)
        # and returning a 500 error is good practice.
        raise HTTPException(status_code=500, detail=f"Failed to read agent.md: {e}")

@app.get("/api/hitl")
async def get_hitl_recommendations() -> List[Dict[str, Any]]:
    """
    Provides a list of Human-in-the-Loop (HITL) recommendations.
    NOTE: This endpoint is not yet implemented and will be connected
    to the core J.A.R.V.I.S. HITL Oracle in a future update.
    """
    raise HTTPException(
        status_code=501,
        detail="HITL endpoint is not yet implemented."
    )


# Mount the Socket.IO application to the FastAPI app
# This allows handling both HTTP and WebSocket traffic
app.mount("/ws", socket_app)

@sio.event
async def connect(sid, environ):
    """
    Event handler for when a client connects to the Socket.IO server.
    """
    print(f"Socket.IO client connected: {sid}")
    await sio.emit('response', {'data': 'Connected to backend!'}, room=sid)

@sio.event
async def disconnect(sid):
    """
    Event handler for when a client disconnects from the Socket.IO server.
    """
    print(f"Socket.IO client disconnected: {sid}")

@sio.on('chat_message')
async def handle_chat_message(sid, data):
    """
    Event handler for 'chat_message' events from the client.
    It echoes the message back to the client.
    """
    print(f"Received message from {sid}: {data}")
    # In a real application, you would process the message here
    # For now, we'll just echo it back
    response_data = f"Message received: {data['message']}"
    await sio.emit('chat_response', {'data': response_data}, room=sid)

if __name__ == "__main__":
    # This block allows running the server directly for development
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000
    )
