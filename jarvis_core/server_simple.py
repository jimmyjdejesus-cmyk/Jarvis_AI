# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/




Copyright (c) 2025 Jimmy De Jesus (Bravetto)

Licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0).
See https://creativecommons.org/licenses/by/4.0/ for license terms.

from __future__ import annotations

from typing import List, Optional

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from .app import AdaptiveMindApplication
from .config import AppConfig
from .logger import get_logger

logger = get_logger(__name__)


class Message(BaseModel):
    role: str = Field(..., description="Role of the speaker")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    messages: List[Message]
    persona: str = Field("generalist", description="Persona to route the request")
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(512, ge=32, le=4096)
    metadata: Optional[dict] = None
    external_context: Optional[List[str]] = None


class ChatResponse(BaseModel):
    content: str
    model: str
    tokens: int
    diagnostics: dict


class HealthResponse(BaseModel):
    status: str
    available_models: List[str]


class OpenAIChatRequest(BaseModel):
    model: str = "adaptivemind-default"
    messages: List[Message]
    temperature: float = 0.7
    max_tokens: int = Field(512, ge=32, le=4096)
    stream: bool = False


class OpenAIChatResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[dict]
    usage: dict


def build_app(config: Optional[AppConfig] = None) -> FastAPI:
    jarvis_app = AdaptiveMindApplication(config=config)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        try:
            yield
        finally:
            jarvis_app.shutdown()

    fastapi_app = FastAPI(title="AdaptiveMind Local Assistant", version="1.0.0", lifespan=lifespan)

    def _verify_api_key(request: Request) -> None:
        if not jarvis_app.config.security.api_keys:
            return
        header_key = request.headers.get("X-API-Key")
        query_key = request.query_params.get("api_key")
        provided = header_key or query_key
        if not provided or provided not in jarvis_app.config.security.api_keys:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    def _app_dependency(request: Request) -> AdaptiveMindApplication:
        _verify_api_key(request)
        return jarvis_app

    @fastapi_app.get("/health", response_model=HealthResponse)
    def health(app: AdaptiveMindApplication = Depends(_app_dependency)) -> HealthResponse:
        models = app.models()
        status_value = "ok" if models else "degraded"
        return HealthResponse(status=status_value, available_models=models)

    @fastapi_app.get("/", response_class=HTMLResponse)
    def index() -> str:
        return _INDEX_HTML

    @fastapi_app.get("/api/v1/models", response_model=List[str])
    def models(app: AdaptiveMindApplication = Depends(_app_dependency)) -> List[str]:
        return app.models()

    @fastapi_app.post("/api/v1/chat", response_model=ChatResponse)
    def chat(request: ChatRequest, app: AdaptiveMindApplication = Depends(_app_dependency)) -> ChatResponse:
        if request.persona not in app.config.personas:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Persona '{request.persona}' not found")

        try:
            payload = app.chat(
                persona=request.persona,
                messages=[message.model_dump() for message in request.messages],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                metadata=request.metadata,
                external_context=request.external_context,
            )
            return ChatResponse(**payload)
        except Exception as e:
            logger.error("Chat request failed", exc_info=e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Chat request failed")

    @fastapi_app.post("/v1/chat/completions")
    def openai_chat_completions(request: OpenAIChatRequest, app: AdaptiveMindApplication = Depends(_app_dependency)) -> OpenAIChatResponse:
        import time

        persona = request.model if request.model in app.config.personas else "generalist"
        
        try:
            payload = app.chat(
                persona=persona,
                messages=[message.model_dump() for message in request.messages],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )

            created = int(time.time())
            choice = {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": payload["content"]
                },
                "finish_reason": "stop"
            }

            return OpenAIChatResponse(
                id=f"chatcmpl-{created}",
                created=created,
                model=payload["model"],
                choices=[choice],
                usage={
                    "prompt_tokens": 10,  # estimated
                    "completion_tokens": payload["tokens"],
                    "total_tokens": 10 + payload["tokens"]
                }
            )
        except Exception as e:
            logger.error("OpenAI chat request failed", exc_info=e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Chat request failed")

    @fastapi_app.get("/v1/models")
    def openai_models(app: AdaptiveMindApplication = Depends(_app_dependency)):
        import time
        return {
            "object": "list",
            "data": [{
                "id": "adaptivemind-local",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "adaptivemind"
            }]
        }

    return fastapi_app


_INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AdaptiveMind Local Assistant</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 2rem; background: #111; color: #f5f5f5; }
        h1 { color: #00e0ff; }
        .container { max-width: 720px; margin: auto; }
        textarea { width: 100%; height: 160px; padding: 1rem; background: #1b1b1b; color: #f5f5f5; border: 1px solid #333; border-radius: 8px; }
        button { padding: 0.5rem; margin-top: 0.5rem; background: #00e0ff; color: #111; border: none; border-radius: 6px; cursor: pointer; }
        pre { white-space: pre-wrap; background: #1b1b1b; padding: 1rem; border-radius: 8px; border: 1px solid #333; }
        label { display: block; margin-top: 1rem; }
        .status { margin-bottom: 1rem; padding: 0.5rem; border-radius: 4px; }
        .status.ok { background: #0f5132; color: #d1e7dd; }
        .status.degraded { background: #664d03; color: #fff3cd; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 AdaptiveMind Local Assistant</h1>
        <div id="status" class="status">Loading...</div>
        <label for="prompt">Ask AdaptiveMind anything:</label>
        <textarea id="prompt" placeholder="Type your question here..."></textarea>
        <button onclick="sendChat()">Send</button>
        <pre id="output">Response will appear here.</pre>
    </div>
    <script>
        async function checkHealth() {
            try {
                const response = await fetch('/health');
                const data = await response.json();
                const statusEl = document.getElementById('status');
                statusEl.textContent = `Status: ${data.status} | Models: ${data.available_models.join(', ')}`;
                statusEl.className = `status ${data.status}`;
            } catch (error) {
                const statusEl = document.getElementById('status');
                statusEl.textContent = 'Status: Error connecting to server';
                statusEl.className = 'status degraded';
            }
        }
        
        async function sendChat() {
            const prompt = document.getElementById('prompt').value;
            if (!prompt.trim()) return;
            
            const output = document.getElementById('output');
            output.textContent = 'Thinking...';
            
            try {
                const response = await fetch('/api/v1/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        persona: 'generalist',
                        messages: [{ role: 'user', content: prompt }]
                    })
                });
                
                if (!response.ok) {
                    output.textContent = 'Error: ' + response.status + ' ' + response.statusText;
                    return;
                }
                
                const data = await response.json();
                output.textContent = data.content + '\\n\\nTokens: ' + data.tokens + '\\nModel: ' + data.model;
            } catch (error) {
                output.textContent = 'Error: ' + error.message;
            }
        }
        
        checkHealth();
        setInterval(checkHealth, 30000); // Check every 30 seconds
    </script>
</body>
</html>
"""

__all__ = ["build_app"]
