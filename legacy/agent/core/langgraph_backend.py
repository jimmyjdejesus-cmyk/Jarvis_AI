"""
Backend API Service for Jarvis AI V2 LangGraph Agent

This FastAPI service provides HTTP endpoints for the LangGraph agent workflow,
enabling the Streamlit frontend to interact with the V2 architecture.
"""

from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import asyncio
from pathlib import Path
import json

try:
    from agent.core.langgraph_agent import get_agent, LANGGRAPH_AVAILABLE
    from agent.core.langchain_tools import get_available_tools, get_tools_description
except ImportError:
    # Fallback when modules are not available
    LANGGRAPH_AVAILABLE = False
    
    def get_agent(**kwargs):
        return None
    
    def get_available_tools():
        return []
    
    def get_tools_description():
        return "Tools not available"


# Pydantic models for API requests/responses
class AgentRequest(BaseModel):
    message: str
    config: Optional[Dict[str, Any]] = None
    use_langgraph: bool = True


class AgentResponse(BaseModel):
    success: bool
    result: Dict[str, Any]
    error: Optional[str] = None
    workflow_steps: Optional[List[str]] = None
    final_message: Optional[str] = None


class StatusResponse(BaseModel):
    service: str
    status: str
    langgraph_available: bool
    tools_count: int
    version: str


class ToolsResponse(BaseModel):
    tools: List[str]
    description: str


# Global agent instance
_agent_instance = None


def get_agent_instance(expert_model: str = "llama3.2"):
    """Get or create the global agent instance."""
    global _agent_instance
    
    if _agent_instance is None:
        try:
            tools = get_available_tools()
            _agent_instance = get_agent(
                expert_model=expert_model,
                tools=tools,
                use_langgraph=LANGGRAPH_AVAILABLE
            )
        except Exception as e:
            print(f"Error creating agent: {e}")
            _agent_instance = None
    
    return _agent_instance


# FastAPI app
app = FastAPI(
    title="Jarvis AI V2 Backend",
    description="LangGraph-based agent API for Jarvis AI",
    version="2.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
# Read allowed origins from environment variable, fallback to ["*"] with warning
allowed_origins_env = os.getenv("CORS_ALLOW_ORIGINS")
if allowed_origins_env:
    allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]
else:
    allowed_origins = ["*"]
    print("WARNING: CORS_ALLOW_ORIGINS environment variable not set. Using wildcard '*' for CORS allow_origins. This is insecure for production!")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=StatusResponse)
async def root():
    """Root endpoint with service status."""
    return StatusResponse(
        service="Jarvis AI V2 Backend",
        status="running",
        langgraph_available=LANGGRAPH_AVAILABLE,
        tools_count=len(get_available_tools()),
        version="2.0.0"
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat() + "Z"}


@app.get("/tools", response_model=ToolsResponse)
async def get_tools():
    """Get available tools and their descriptions."""
    tools = get_available_tools()
    tool_names = [tool.__name__ for tool in tools]
    
    return ToolsResponse(
        tools=tool_names,
        description=get_tools_description()
    )


@app.post("/agent/invoke", response_model=AgentResponse)
async def invoke_agent(request: AgentRequest):
    """
    Invoke the LangGraph agent with a user message.
    
    Args:
        request: AgentRequest containing message and optional config
        
    Returns:
        AgentResponse with the workflow result
    """
    try:
        agent = get_agent_instance()
        
        if agent is None:
            return AgentResponse(
                success=False,
                result={},
                error="Agent not available. Check LangGraph installation."
            )
        
        # Execute the agent workflow
        result = agent.invoke(request.message, config=request.config)
        
        # Extract workflow information
        workflow_steps = []
        final_message = ""
        
        if isinstance(result, dict):
            # Extract messages from the result
            messages = result.get("messages", [])
            if messages:
                final_message = str(messages[-1].content if hasattr(messages[-1], 'content') else messages[-1])
            
            # Extract workflow steps
            current_step = result.get("current_step")
            if current_step:
                workflow_steps.append(current_step)
        
        return AgentResponse(
            success=True,
            result=result,
            workflow_steps=workflow_steps,
            final_message=final_message
        )
    
    except Exception as e:
        return AgentResponse(
            success=False,
            result={},
            error=str(e)
        )


@app.post("/agent/stream")
async def stream_agent_response(request: AgentRequest):
    """
    Stream agent responses for real-time updates.
    Note: This is a placeholder for streaming functionality.
    """
    # Placeholder for streaming implementation
    # In a real implementation, this would use Server-Sent Events or WebSockets
    agent = get_agent_instance()
    
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not available")
    
    try:
        result = agent.invoke(request.message, config=request.config)
        return {"status": "complete", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agent/status")
async def get_agent_status():
    """Get current agent status and configuration."""
    agent = get_agent_instance()
    
    return {
        "agent_available": agent is not None,
        "langgraph_available": LANGGRAPH_AVAILABLE,
        "tools_available": len(get_available_tools()),
        "expert_model": getattr(agent, 'expert_model', 'unknown') if agent else None,
    }


@app.post("/agent/reset")
async def reset_agent():
    """Reset the agent instance (clear memory/state)."""
    global _agent_instance
    _agent_instance = None
    
    return {"status": "Agent reset successfully"}


# Configuration endpoints
@app.get("/config")
async def get_config():
    """Get current API configuration."""
    return {
        "langgraph_available": LANGGRAPH_AVAILABLE,
        "default_model": "llama3.2",
        "max_iterations": 15,
        "tools_enabled": True,
    }


@app.post("/config")
async def update_config(config: Dict[str, Any]):
    """Update API configuration."""
    # In a real implementation, this would update global configuration
    return {"status": "Configuration updated", "config": config}


# Workflow visualization endpoints (for LangGraphUI integration)
@app.get("/workflow/graph")
async def get_workflow_graph():
    """Get the workflow graph structure for visualization."""
    # This would return the graph structure for LangGraphUI
    return {
        "nodes": [
            {"id": "planner", "type": "planner", "label": "Planner"},
            {"id": "code_writer", "type": "code_writer", "label": "Code Writer"},
            {"id": "debugger", "type": "debugger", "label": "Debugger"},
            {"id": "tool_executor", "type": "tool_executor", "label": "Tool Executor"},
            {"id": "git_manager", "type": "git_manager", "label": "Git Manager"},
            {"id": "critic", "type": "critic", "label": "Critic"},
        ],
        "edges": [
            {"from": "planner", "to": "code_writer", "condition": "requires_code"},
            {"from": "planner", "to": "tool_executor", "condition": "requires_tools"},
            {"from": "planner", "to": "git_manager", "condition": "requires_git"},
            {"from": "code_writer", "to": "debugger", "condition": "has_code"},
            {"from": "debugger", "to": "critic", "condition": "tests_passed"},
            {"from": "tool_executor", "to": "critic", "condition": "tools_executed"},
            {"from": "git_manager", "to": "critic", "condition": "git_completed"},
            {"from": "critic", "to": "planner", "condition": "continue_workflow"},
        ]
    }


@app.get("/workflow/history/{session_id}")
async def get_workflow_history(session_id: str):
    """Get workflow execution history for a session."""
    # Placeholder for workflow history retrieval
    return {
        "session_id": session_id,
        "executions": [],
        "total": 0
    }


# Error handling
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected exceptions."""
    return {
        "error": "Internal server error",
        "detail": str(exc),
        "type": type(exc).__name__
    }


def create_app() -> FastAPI:
    """Factory function to create the FastAPI app."""
    return app


def run_server(host: str = "0.0.0.0", port: int = 8001, reload: bool = False):
    """Run the backend server."""
    print(f"Starting Jarvis AI V2 Backend on {host}:{port}")
    print(f"LangGraph available: {LANGGRAPH_AVAILABLE}")
    print(f"Tools available: {len(get_available_tools())}")
    
    uvicorn.run(
        "agent.core.langgraph_backend:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    run_server(reload=True)