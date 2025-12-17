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

import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, ValidationError

from .app import AdaptiveMindApplication
from .config import AppConfig
from .logger import get_logger

logger = get_logger(__name__)


# Custom exception classes for better error handling
class ValidationErrorResponse(BaseModel):
    """Standardized validation error response."""
    error: str
    message: str
    details: Optional[List[Dict[str, Any]]] = None
    timestamp: str
    status_code: int = 422


class APIErrorResponse(BaseModel):
    """Standardized API error response."""
    error: str
    message: str
    timestamp: str
    status_code: int


def create_error_response(error: str, message: str, status_code: int, details: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Create a standardized error response."""
    return {
        "error": error,
        "message": message,
        "status_code": status_code,
        "timestamp": datetime.now().isoformat(),
        "details": details
    }


def build_app(config: Optional[AppConfig] = None) -> FastAPI:
    jarvis_app = AdaptiveMindApplication(config=config)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        try:
            yield
        finally:
            jarvis_app.shutdown()

    fastapi_app = FastAPI(title="AdaptiveMind Local Assistant", version="1.0.0", lifespan=lifespan)

    # Add custom exception handlers for proper status code handling
    @fastapi_app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle validation errors with proper HTTP 422 status code."""
        error_details = []
        for error in exc.errors():
            field = ".".join(str(x) for x in error["loc"] if x != "body")
            error_details.append({
                "field": field,
                "message": error["msg"],
                "type": error["type"]
            })
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=create_error_response(
                error="ValidationError",
                message="Request validation failed",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                details=error_details
            )
        )

    @fastapi_app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions with standardized response format."""
        return JSONResponse(
            status_code=exc.status_code,
            content=create_error_response(
                error="HTTPException",
                message=exc.detail,
                status_code=exc.status_code
            )
        )

    @fastapi_app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions with proper error logging."""
        logger.error("Unhandled exception", exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=create_error_response(
                error="InternalServerError",
                message="An unexpected error occurred",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        )

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
        # (ADAPTIVEMIND_TEST_MODE=true).
        if ExceptionMiddleware is None and os.getenv("ADAPTIVEMIND_TEST_MODE", "false").lower() == "true":
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

    def _app_dependency(request: Request) -> AdaptiveMindApplication:
        _verify_api_key(request)
        return jarvis_app

    @fastapi_app.get("/health", response_model=dict)
    def health(app: AdaptiveMindApplication = Depends(_app_dependency)) -> dict:
        models = app.models()
        status_value = "ok" if models else "degraded"
        return {
            "status": status_value,
            "available_models": models,
            "timestamp": datetime.now().isoformat()
        }

    @fastapi_app.get("/", response_class=HTMLResponse)
    def index() -> str:
        return _OLLAMA_UI_HTML

    @fastapi_app.get("/api/v1/models", response_model=List[str])
    def models(app: AdaptiveMindApplication = Depends(_app_dependency)) -> List[str]:
        return app.models()

    @fastapi_app.get("/api/v1/personas")
    def personas(app: AdaptiveMindApplication = Depends(_app_dependency)) -> List[dict]:
        try:
            return app.personas()
        except Exception as e:
            logger.error("Failed to retrieve personas", exc_info=e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve personas")

    @fastapi_app.post("/api/v1/chat")
    def chat(request: dict, app: AdaptiveMindApplication = Depends(_app_dependency)) -> dict:
        """Enhanced chat endpoint with better error handling."""
        # Extract and validate request data manually for better control
        try:
            messages = request.get("messages", [])
            persona = request.get("persona", "generalist")
            temperature = request.get("temperature", 0.7)
            max_tokens = request.get("max_tokens",  = request.get("512)
            metadatametadata")
            external_context = request.get("external_context")
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Invalid request format: {str(e)}"
            )

        # Validate persona exists
        if persona not in app.config.personas:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Persona '{persona}' not found. Available: {list(app.config.personas.keys())}"
            )

        # Validate required fields
        if not messages or not isinstance(messages, list):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Messages field is required and must be a list"
            )

        # Validate temperature range
        if not isinstance(temperature, (int, float)) or not (0.0 <= temperature <= 2.0):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Temperature must be a number between 0.0 and 2.0"
            )

        # Validate max_tokens range
        if not isinstance(max_tokens, int) or not (32 <= max_tokens <= 4096):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="max_tokens must be an integer between 32 and 4096"
            )

        try:
            payload = app.chat(
                persona=persona,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                metadata=metadata,
                external_context=external_context,
            )
            return {
                "content": payload["content"],
                "model": payload["model"],
                "tokens": payload["tokens"],
                "diagnostics": payload["diagnostics"]
            }
        except Exception as e:
            logger.error("Chat request failed", exc_info=e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Chat request failed")

    @fastapi_app.get("/api/v1/monitoring/metrics")
    def metrics(app: AdaptiveMindApplication = Depends(_app_dependency)) -> dict:
        try:
            return {"history": app.metrics_snapshot()}
        except Exception as e:
            logger.error("Failed to retrieve metrics", exc_info=e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve metrics")

    @fastapi_app.get("/api/v1/monitoring/traces")
    def traces(app: AdaptiveMindApplication = Depends(_app_dependency)) -> dict:
        try:
            return {"traces": app.traces_latest()}
        except Exception as e:
            logger.error("Failed to retrieve traces", exc_info=e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve traces")

    # Management API endpoints
    @fastapi_app.get("/api/v1/management/system/status")
    def get_system_status(app: AdaptiveMindApplication = Depends(_app_dependency)) -> dict:
        return app.system_status()

    @fastapi_app.get("/api/v1/management/routing/config")
    def get_routing_config(app: AdaptiveMindApplication = Depends(_app_dependency)) -> dict:
        return app.get_routing_config()

    @fastapi_app.get("/api/v1/management/backends")
    def list_backends(app: AdaptiveMindApplication = Depends(_app_dependency)) -> dict:
        return {"backends": app.list_backends()}

    @fastapi_app.get("/api/v1/management/context/config")
    def get_context_config(app: AdaptiveMindApplication = Depends(_app_dependency)) -> dict:
        return app.get_context_config()

    @fastapi_app.get("/api/v1/management/security/status")
    def get_security_status(app: AdaptiveMindApplication = Depends(_app_dependency)) -> dict:
        return app.get_security_status()

    # Phase 2: Mutation endpoints
    @fastapi_app.post("/api/v1/management/personas")
    def create_persona(request: dict, app: AdaptiveMindApplication = Depends(_app_dependency)) -> dict:
        try:
            result = app.create_persona(request)
            return result
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            logger.error("Failed to create persona", exc_info=e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create persona")

    @fastapi_app.put("/api/v1/management/personas/{name}")
    def update_persona(name: str, request: dict, app: AdaptiveMindApplication = Depends(_app_dependency)) -> dict:
        try:
            result = app.update_persona(name, request)
            return result
        except ValueError as e:
            if "not found" in str(e):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to update persona '{name}'", exc_info=e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update persona '{name}'")

    @fastapi_app.delete("/api/v1/management/personas/{name}")
    def delete_persona(name: str, app: AdaptiveMindApplication = Depends(_app_dependency)) -> dict:
        try:
            app.delete_persona(name)
            return {"message": f"Persona '{name}' deleted successfully"}
        except ValueError as e:
            if "not found" in str(e):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to delete persona '{name}'", exc_info=e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete persona '{name}'")

    @fastapi_app.put("/api/v1/management/config/routing")
    def update_routing_config(request: dict, app: AdaptiveMindApplication = Depends(_app_dependency)) -> dict:
        try:
            result = app.update_routing_config(request)
            return result
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            logger.error("Failed to update routing config", exc_info=e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update routing config")

    @fastapi_app.put("/api/v1/management/config/context")
    def update_context_config(request: dict, app: AdaptiveMindApplication = Depends(_app_dependency)) -> dict:
        try:
            result = app.update_context_config(request)
            return result
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            logger.error("Failed to update context config", exc_info=e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update context config")

    @fastapi_app.post("/api/v1/management/backends/{name}/test")
    def test_backend(name: str, app: AdaptiveMindApplication = Depends(_app_dependency)) -> dict:
        try:
            result = app.test_backend(name)
            return result
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to test backend '{name}'", exc_info=e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to test backend '{name}'")

    @fastapi_app.post("/api/v1/management/config/save")
    def save_config(app: AdaptiveMindApplication = Depends(_app_dependency)) -> dict:
        try:
            result = app.save_config()
            return result
        except Exception as e:
            logger.error("Failed to save config", exc_info=e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save configuration")

    # OpenAI-compatible endpoints
    @fastapi_app.post("/v1/chat/completions")
    def openai_chat_completions(request: dict, app: AdaptiveMindApplication = Depends(_app_dependency)) -> dict:
        import time

        # Extract OpenAI request data
        model = request.get("model", "adaptivemind-default")
        messages = request.get("messages", [])
        temperature = request.get("temperature", 0.7)
        max_tokens = request.get("max_tokens", 512)

        # Convert OpenAI format to Jarvis format
        persona = model if model in app.config.personas else "generalist"

        # Estimate prompt tokens if not provided by Jarvis
        prompt_text = " ".join([msg.get("content", "") for msg in messages if isinstance(msg, dict)])
        estimated_prompt_tokens = len(prompt_text) // 4  # Rough approximation: ~4 chars per token

        try:
            # Call Jarvis chat
            payload = app.chat(
                persona=persona,
                messages=messages,
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

            return {
                "id": f"chatcmpl-{created}",
                "created": created,
                "model": payload["model"],
                "object": "chat.completion",
                "choices": [choice],
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens
                }
            }
        except Exception as e:
            logger.error("OpenAI chat completion failed", exc_info=e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Chat completion failed")

    @fastapi_app.get("/v1/models")
    def openai_models(app: AdaptiveMindApplication = Depends(_app_dependency)):
        import time
        # Return hardcoded models
        data = [{
            "id": "llama3.2:latest",
            "object": "model",
            "created": int(time.time()),
            "owned_by": "adaptivemind"
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
    <title>AdaptiveMind Ollama Console</title>
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
        <h1>AdaptiveMind Ollama Console</h1>
        <p>Local-first assistant with deep research, persona routing, and secure API key gating.</p>
        <label for="persona">Persona</label>
        <select id="persona"></select>
        <label for="prompt">Prompt</label>
        <textarea id="prompt" placeholder="Ask AdaptiveMind anything..."></textarea>
        <button onclick="sendChat()">Send</button>
        <pre id="output">Response will appear here.</pre>
    </div>
    <script>
        async function loadPersonas() {
            try {
                const response = await fetch('/api/v1/personas');
                const personas = await response.json();
                const select = document.getElementById('persona');
                personas.forEach(p => {
                    const option = document.createElement('option');
                    option.value = p.name;
                    option.textContent = `${p.name} — ${p.description}`;
                    select.appendChild(option);
                });
            } catch (e) {
                console.error('Failed to load personas:', e);
            }
        }
        async function sendChat() {
            const prompt = document.getElementById('prompt').value;
            const persona = document.getElementById('persona').value || 'generalist';
            const body = {
                persona,
                messages: [
                    { role: 'user', content: prompt }
                { objective: ' ],
                metadata:ui-chat' }
            };
            try {
                const response = await fetch('/api/v1/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(body)
                });
                if (!response.ok) {
                    const errorData = await response.json();
                    document.getElementById('output').textContent = `Request failed: ${response.status} - ${errorData.message || errorData.detail}`;
                    return;
                }
                const data = await response.json();
                document.getElementById('output').textContent = data.content + '\\n\\nTokens: ' + data.tokens + '\\nModel: ' + data.model;
            } catch (e) {
                document.getElementById('output').textContent = 'Request failed: ' + e.message;
            }
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
    
    port = int(os.getenv("ADAPTIVEMIND_PORT", 8000))
    host = os.getenv("ADAPTIVEMIND_HOST", "0.0.0.0")
    
    # Initialize config
    from .config import load_config
    config = load_config()
    
    app = build_app(config)
    
    uvicorn.run(app, host=host, port=port)
