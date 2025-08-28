"""Minimal FastAPI application exposing knowledge graph endpoints."""
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm

from .auth import Token, login_for_access_token, role_required
from .knowledge_graph import knowledge_graph

app = FastAPI()

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

@app.get("/health")
def get_health() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}
