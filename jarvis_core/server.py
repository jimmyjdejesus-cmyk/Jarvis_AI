# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



from __future__ import annotations

import json
from typing import List, Optional

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel, Field

from .app import JarvisApplication
from .config import AppConfig
from .logger import get_logger

logger = get_logger(__name__)


class Message(BaseModel):
    role: str = Field(..., description="Role of the speaker")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    messages: List[Message]
    persona: str = Field("generalist", description="Persona to route the request")
    # Constrain temperature to sensible range for the model
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


class MetricsResponse(BaseModel):
    history: List[dict]


class TracesResponse(BaseModel):
    traces: List[dict]


class OpenAIChatRequest(BaseModel):
    model: str = "jarvis-default"
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


class OpenAIModel(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str = "jarvis"


class OpenAIModelsResponse(BaseModel):
    object: str = "list"
    data: List[OpenAIModel]


# Management API Models --------------------------------------------------

class ComponentHealth(BaseModel):
    name: str
    status: str  # "healthy", "degraded", "unhealthy"
    details: Optional[dict] = None


class SystemStatusResponse(BaseModel):
    status: str  # "healthy", "degraded", "unhealthy"
    uptime_seconds: float
    version: str
    active_backends: List[str]
    active_personas: List[str]
    config_hash: str  # For detecting config changes


class RoutingConfigResponse(BaseModel):
    allowed_personas: List[str]
    enable_adaptive_routing: bool = True


class BackendStatus(BaseModel):
    name: str
    type: str  # "ollama", "windowsml", "fallback"
    is_available: bool
    last_checked: Optional[float] = None  # timestamp
    config: dict  # Backend-specific config


class BackendListResponse(BaseModel):
    backends: List[BackendStatus]


class ContextConfigResponse(BaseModel):
    extra_documents_dir: Optional[str]
    enable_semantic_chunking: bool
    max_combined_context_tokens: int


class APIKeyInfo(BaseModel):
    hash: str  # SHA256 hash
    created_at: Optional[float] = None  # timestamp
    last_used: Optional[float] = None  # timestamp


class SecurityStatusResponse(BaseModel):
    api_keys_count: int
    audit_log_enabled: bool


# Phase 2: Mutation API Models ------------------------------------------

class PersonaCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, pattern=r'^[a-zA-Z0-9_-]+$')
    description: str = Field(..., min_length=1, max_length=200)
    system_prompt: str = Field(..., min_length=1)
    max_context_window: int = Field(4096, ge=512, le=32768)
    routing_hint: str = Field("general", min_length=1, max_length=50)


class PersonaUpdateRequest(BaseModel):
    description: Optional[str] = Field(None, min_length=1, max_length=200)
    system_prompt: Optional[str] = Field(None, min_length=1)
    max_context_window: Optional[int] = Field(None, ge=512, le=32768)
    routing_hint: Optional[str] = Field(None, min_length=1, max_length=50)


class PersonaResponse(BaseModel):
    name: str
    description: str
    system_prompt: str
    max_context_window: int
    routing_hint: str
    is_active: bool


class RoutingConfigUpdateRequest(BaseModel):
    allowed_personas: Optional[List[str]] = None
    enable_adaptive_routing: Optional[bool] = None


class ContextConfigUpdateRequest(BaseModel):
    extra_documents_dir: Optional[str] = None
    enable_semantic_chunking: Optional[bool] = None
    max_combined_context_tokens: Optional[int] = Field(None, ge=1024, le=65536)


class BackendTestResponse(BaseModel):
    success: bool
    latency_ms: Optional[float] = None
    error: Optional[str] = None


class ConfigSaveResponse(BaseModel):
    success: bool
    config_hash: str
    message: str


def build_app(config: Optional[AppConfig] = None) -> FastAPI:
    jarvis_app = JarvisApplication(config=config)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        try:
            yield
        finally:
            jarvis_app.shutdown()

    fastapi_app = FastAPI(title="Jarvis Local Assistant", version="1.0.0", lifespan=lifespan)

    # Compatibility: Normalize middleware entries for Starlette/FastAPI versions
    try:
        normalized = []
        for mw in list(fastapi_app.user_middleware):
            if isinstance(mw, tuple) and len(mw) == 2:
                normalized.append(mw)
            else:
                cls = getattr(mw, "cls", None)
                options = getattr(mw, "kwargs", {})
                normalized.append((cls, options))
        fastapi_app.user_middleware = normalized
    except Exception:
        pass

    # Ensure FastAPI.build_middleware_stack accepts different starlette Middleware shapes
    try:
        # Use safe imports so the compatibility wrapper doesn't fail due to missing
        # modules across different FastAPI/Starlette versions.
        try:
            from starlette.middleware.errors import ServerErrorMiddleware, ExceptionMiddleware  # type: ignore
        except Exception:
            ServerErrorMiddleware = None
            ExceptionMiddleware = None
        try:
            from fastapi.middleware.asyncexitstack import AsyncExitStackMiddleware  # type: ignore
        except Exception:
            AsyncExitStackMiddleware = None

        # Provide a minimal ExceptionMiddleware fallback (if missing in starlette).
        # This is only enabled during tests when requested via environment
        # (JARVIS_TEST_MODE=true).
        if ExceptionMiddleware is None and os.getenv("JARVIS_TEST_MODE", "false").lower() == "true":
            from fastapi import HTTPException as FastAPIHTTPException
            from starlette.responses import JSONResponse

            class ExceptionMiddleware:  # type: ignore
                def __init__(self, app, handlers=None, debug: bool = False):
                    self.app = app
                    self.handlers = handlers or {}
                    self.debug = debug

                async def __call__(self, scope, receive, send):
                    try:
                        await self.app(scope, receive, send)
                    except FastAPIHTTPException as exc:
                        resp = JSONResponse({"detail": exc.detail}, status_code=exc.status_code)
                        await resp(scope, receive, send)
                    except Exception:
                        raise

        def build_middleware_stack_compat(self):
            error_handler = None
            exception_handlers = {}
            for key, value in self.exception_handlers.items():
                if key in (500, Exception):
                    error_handler = value
                else:
                    exception_handlers[key] = value

            debug = self.debug
            # Build a list of normalized middleware entries as tuples (cls, args, kwargs)
            middleware_raw = []
            if ServerErrorMiddleware is not None:
                middleware_raw.append((ServerErrorMiddleware, (), {'handler': error_handler, 'debug': debug}))
            # Extend with any user middleware (already normalized to 2- or 3-tuples)
            middleware_raw += list(self.user_middleware)
            if ExceptionMiddleware is not None:
                middleware_raw.append((ExceptionMiddleware, (), {'handlers': exception_handlers, 'debug': debug}))
            if AsyncExitStackMiddleware is not None:
                middleware_raw.append((AsyncExitStackMiddleware, (), {}))

            normalized = []
            for mw in middleware_raw:
                # Normalize to (cls, args, kwargs) where args is an empty tuple if none
                if isinstance(mw, tuple):
                    if len(mw) == 3:
                        normalized.append(mw)
                    elif len(mw) == 2:
                        cls, options = mw
                        normalized.append((cls, (), options))
                    else:
                        # Unknown shape, try to read properties
                        cls = getattr(mw, 'cls', None)
                        options = getattr(mw, 'kwargs', {})
                        normalized.append((cls, (), options))
                else:
                    cls = getattr(mw, 'cls', None)
                    args = getattr(mw, 'args', ()) or ()
                    options = getattr(mw, 'kwargs', {})
                    normalized.append((cls, args, options))

            app_obj = self.router
            for cls, args, options in reversed(normalized):
                if cls is None:
                    continue
                app_obj = cls(app=app_obj, *args, **(options or {}))
            return app_obj

        import types
        fastapi_app.build_middleware_stack = types.MethodType(build_middleware_stack_compat, fastapi_app)
    except Exception:
        pass

    def _verify_api_key(request: Request) -> None:
        if not jarvis_app.config.security.api_keys:
            return
        header_key = request.headers.get("X-API-Key")
        query_key = request.query_params.get("api_key")
        provided = header_key or query_key
        if not provided or provided not in jarvis_app.config.security.api_keys:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    def _app_dependency(request: Request) -> JarvisApplication:
        _verify_api_key(request)
        return jarvis_app

    @fastapi_app.get("/health", response_model=HealthResponse)
    def health(app: JarvisApplication = Depends(_app_dependency)) -> HealthResponse:
        models = app.models()
        status_value = "ok" if models else "degraded"
        return HealthResponse(status=status_value, available_models=models)

    @fastapi_app.get("/", response_class=HTMLResponse)
    def index() -> str:
        return _OLLAMA_UI_HTML

    @fastapi_app.get("/api/v1/models", response_model=List[str])
    def models(app: JarvisApplication = Depends(_app_dependency)) -> List[str]:
        return app.models()

    @fastapi_app.get("/api/v1/personas", response_model=List[dict])
    def personas(app: JarvisApplication = Depends(_app_dependency)) -> List[dict]:
        try:
            return app.personas()
        except Exception as e:
            logger.error("Failed to retrieve personas", exc_info=e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve personas")

    @fastapi_app.post("/api/v1/chat", response_model=ChatResponse)
    def chat(request: ChatRequest, app: JarvisApplication = Depends(_app_dependency)) -> ChatResponse:
        # Validate persona exists
        if request.persona not in app.config.personas:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Persona '{request.persona}' not found. Available: {list(app.config.personas.keys())}")

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



    @fastapi_app.get("/api/v1/monitoring/metrics", response_model=MetricsResponse)
    def metrics(app: JarvisApplication = Depends(_app_dependency)) -> MetricsResponse:
        try:
            return MetricsResponse(history=app.metrics_snapshot())
        except Exception as e:
            logger.error("Failed to retrieve metrics", exc_info=e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve metrics")

    @fastapi_app.get("/api/v1/monitoring/traces", response_model=TracesResponse)
    def traces(app: JarvisApplication = Depends(_app_dependency)) -> TracesResponse:
        try:
            return TracesResponse(traces=app.traces_latest())
        except Exception as e:
            logger.error("Failed to retrieve traces", exc_info=e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve traces")

    # Management API endpoints -------------------------------------------

    @fastapi_app.get("/api/v1/management/system/status", response_model=SystemStatusResponse)
    def get_system_status(app: JarvisApplication = Depends(_app_dependency)) -> SystemStatusResponse:
        return SystemStatusResponse(**app.system_status())

    @fastapi_app.get("/api/v1/management/routing/config", response_model=RoutingConfigResponse)
    def get_routing_config(app: JarvisApplication = Depends(_app_dependency)) -> RoutingConfigResponse:
        return RoutingConfigResponse(**app.get_routing_config())

    @fastapi_app.get("/api/v1/management/backends", response_model=BackendListResponse)
    def list_backends(app: JarvisApplication = Depends(_app_dependency)) -> BackendListResponse:
        return BackendListResponse(backends=app.list_backends())

    @fastapi_app.get("/api/v1/management/context/config", response_model=ContextConfigResponse)
    def get_context_config(app: JarvisApplication = Depends(_app_dependency)) -> ContextConfigResponse:
        return ContextConfigResponse(**app.get_context_config())

    @fastapi_app.get("/api/v1/management/security/status", response_model=SecurityStatusResponse)
    def get_security_status(app: JarvisApplication = Depends(_app_dependency)) -> SecurityStatusResponse:
        return SecurityStatusResponse(**app.get_security_status())

    # Phase 2: Mutation endpoints -------------------------------------------

    @fastapi_app.post("/api/v1/management/personas", response_model=PersonaResponse)
    def create_persona(request: PersonaCreateRequest, app: JarvisApplication = Depends(_app_dependency)) -> PersonaResponse:
        try:
            result = app.create_persona(request.model_dump())
            return PersonaResponse(**result)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            logger.error("Failed to create persona", exc_info=e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create persona")

    @fastapi_app.put("/api/v1/management/personas/{name}", response_model=PersonaResponse)
    def update_persona(name: str, request: PersonaUpdateRequest, app: JarvisApplication = Depends(_app_dependency)) -> PersonaResponse:
        try:
            result = app.update_persona(name, request.model_dump(exclude_unset=True))
            return PersonaResponse(**result)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND if "not found" in str(e) else status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to update persona '{name}'", exc_info=e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update persona '{name}'")

    @fastapi_app.delete("/api/v1/management/personas/{name}")
    def delete_persona(name: str, app: JarvisApplication = Depends(_app_dependency)):
        try:
            app.delete_persona(name)
            return {"message": f"Persona '{name}' deleted successfully"}
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND if "not found" in str(e) else status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to delete persona '{name}'", exc_info=e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete persona '{name}'")

    @fastapi_app.put("/api/v1/management/config/routing", response_model=RoutingConfigResponse)
    def update_routing_config(request: RoutingConfigUpdateRequest, app: JarvisApplication = Depends(_app_dependency)) -> RoutingConfigResponse:
        try:
            result = app.update_routing_config(request.model_dump(exclude_unset=True))
            return RoutingConfigResponse(**result)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            logger.error("Failed to update routing config", exc_info=e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update routing config")

    @fastapi_app.put("/api/v1/management/config/context", response_model=ContextConfigResponse)
    def update_context_config(request: ContextConfigUpdateRequest, app: JarvisApplication = Depends(_app_dependency)) -> ContextConfigResponse:
        try:
            result = app.update_context_config(request.model_dump(exclude_unset=True))
            return ContextConfigResponse(**result)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            logger.error("Failed to update context config", exc_info=e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update context config")

    @fastapi_app.post("/api/v1/management/backends/{name}/test", response_model=BackendTestResponse)
    def test_backend(name: str, app: JarvisApplication = Depends(_app_dependency)) -> BackendTestResponse:
        try:
            result = app.test_backend(name)
            return BackendTestResponse(**result)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to test backend '{name}'", exc_info=e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to test backend '{name}'")

    @fastapi_app.post("/api/v1/management/config/save", response_model=ConfigSaveResponse)
    def save_config(app: JarvisApplication = Depends(_app_dependency)) -> ConfigSaveResponse:
        try:
            result = app.save_config()
            return ConfigSaveResponse(**result)
        except Exception as e:
            logger.error("Failed to save config", exc_info=e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save configuration")

    # OpenAI-compatible endpoints
    @fastapi_app.post("/v1/chat/completions")
    def openai_chat_completions(request: OpenAIChatRequest, app: JarvisApplication = Depends(_app_dependency)) -> OpenAIChatResponse:
        import time

        # Convert OpenAI format to Jarvis format
        persona = request.model if request.model in app.config.personas else "generalist"
        messages = request.messages
        temperature = request.temperature
        max_tokens = request.max_tokens

        # Estimate prompt tokens if not provided by Jarvis
        prompt_text = " ".join([msg.content for msg in messages if hasattr(msg, 'content')])
        estimated_prompt_tokens = len(prompt_text) // 4  # Rough approximation: ~4 chars per token

        # Call Jarvis chat
        payload = app.chat(
            persona=persona,
            messages=[message.model_dump() for message in messages],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Convert Jarvis response to OpenAI format
        created = int(time.time())
        choice = {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": payload["content"]
            },
            "finish_reason": "stop"
        }

        # Use actual context tokens if available, otherwise estimate
        prompt_tokens = payload.get("context_tokens", estimated_prompt_tokens)
        completion_tokens = payload["tokens"]

        return OpenAIChatResponse(
            id=f"chatcmpl-{created}",
            created=created,
            model=payload["model"],
            choices=[choice],
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens
            }
        )

    @fastapi_app.get("/v1/models")
    def openai_models(app: JarvisApplication = Depends(_app_dependency)):
        import time
        # For now, return hardcoded models
        data = [{
            "id": "llama3.2:latest",
            "object": "model",
            "created": int(time.time()),
            "owned_by": "jarvis"
        }]
        return {
            "object": "list",
            "data": data
        }

    return fastapi_app


_OLLAMA_UI_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Jarvis Ollama Console</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 2rem; background: #111; color: #f5f5f5; }
        h1 { color: #00e0ff; }
        .container { max-width: 720px; margin: auto; }
        textarea { width: 100%; height: 160px; padding: 1rem; background: #1b1b1b; color: #f5f5f5; border: 1px solid #333; border-radius: 8px; }
        select, button { padding: 0.5rem; margin-top: 0.5rem; background: #00e0ff; color: #111; border: none; border-radius: 6px; cursor: pointer; }
        pre { white-space: pre-wrap; background: #1b1b1b; padding: 1rem; border-radius: 8px; border: 1px solid #333; }
        label { display: block; margin-top: 1rem; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Jarvis Ollama Console</h1>
        <p>Local-first assistant with deep research, persona routing, and secure API key gating.</p>
        <label for="persona">Persona</label>
        <select id="persona"></select>
        <label for="prompt">Prompt</label>
        <textarea id="prompt" placeholder="Ask Jarvis anything..."></textarea>
        <button onclick="sendChat()">Send</button>
        <pre id="output">Response will appear here.</pre>
    </div>
    <script>
        async function loadPersonas() {
            const response = await fetch('/api/v1/personas');
            const personas = await response.json();
            const select = document.getElementById('persona');
            personas.forEach(p => {
                const option = document.createElement('option');
                option.value = p.name;
                option.textContent = `${p.name} — ${p.description}`;
                select.appendChild(option);
            });
        }
        async function sendChat() {
            const prompt = document.getElementById('prompt').value;
            const persona = document.getElementById('persona').value || 'generalist';
            const body = {
                persona,
                messages: [
                    { role: 'user', content: prompt }
                ],
                metadata: { objective: 'ui-chat' }
            };
            const response = await fetch('/api/v1/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            if (!response.ok) {
                document.getElementById('output').textContent = 'Request failed: ' + response.status;
                return;
            }
            const data = await response.json();
            document.getElementById('output').textContent = data.content + '\n\nTokens: ' + data.tokens + '\nModel: ' + data.model;
        }
        loadPersonas();
    </script>
</body>
</html>
"""


__all__ = ["build_app"]

if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.getenv("JARVIS_PORT", 8000))
    host = os.getenv("JARVIS_HOST", "0.0.0.0")
    
    # Initialize config
    from .config import load_config
    config = load_config()
    
    app = build_app(config)
    
    uvicorn.run(app, host=host, port=port)
