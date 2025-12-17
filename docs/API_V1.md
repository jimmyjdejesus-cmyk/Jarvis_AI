
Copyright (c) 2025 Jimmy De Jesus (Bravetto)

Licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0).
See https://creativecommons.org/licenses/by/4.0/ for license terms.

# AdaptiveMind AI API v1 Reference

This document describes the currently implemented API endpoints.

**Base URL:** `http://127.0.0.1:8000`
**Auth:** `X-API-Key: <ADAPTIVEMIND_API_KEY>` header (set `ADAPTIVEMIND_DISABLE_AUTH=true` to bypass locally)

---

## Health

### GET `/health`
Check API health and available models.

**Response:**
```json
{
  "status": "ok",
  "available_models": ["ollama", "openrouter", "windowsml", "contextual-fallback"]
}
```

---

## Core API

### GET `/api/v1/models`
List available model backends.

**Response:**
```json
["ollama", "openrouter", "windowsml", "contextual-fallback"]
```

### GET `/api/v1/personas`
List all configured personas.

**Response:**
```json
[
  {
    "name": "generalist",
    "description": "General purpose assistant",
    "max_context_window": 4096,
    "routing_hint": "general"
  }
]
```

### POST `/api/v1/chat`
Generate a chat response using the specified persona.

**Request:**
```json
{
  "messages": [{"role": "user", "content": "Hello!"}],
  "persona": "generalist",
  "temperature": 0.7,
  "max_tokens": 512,
  "metadata": {},
  "external_context": []
}
```

**Response:**
```json
{
  "content": "Hello! How can I help you today?",
  "model": "ollama",
  "tokens": 15,
  "diagnostics": {}
}
```

---

## Monitoring

### GET `/api/v1/monitoring/metrics`
Get historical performance metrics.

**Response:**
```json
{
  "history": [
    {
      "request_count": 150,
      "average_latency_ms": 245.6,
      "max_latency_ms": 890.2,
      "tokens_generated": 5000,
      "context_tokens": 12000,
      "personas_used": ["generalist"]
    }
  ]
}
```

### GET `/api/v1/monitoring/traces`
Get recent request traces for debugging.

**Response:**
```json
{
  "traces": [
    {
      "persona": "generalist",
      "backend": "ollama",
      "latency_ms": 234.5,
      "tokens": 50,
      "timestamp": "2025-12-15T12:34:35Z"
    }
  ]
}
```

---

## Management API

### GET `/api/v1/management/system/status`
Get comprehensive system status.

**Response:**
```json
{
  "status": "healthy",
  "uptime_seconds": 3600.5,
  "version": "1.0.0",
  "active_backends": ["ollama", "openrouter"],
  "active_personas": ["generalist", "researcher"],
  "config_hash": "a1b2c3d4e5f6g7h8"
}
```

### GET `/api/v1/management/routing/config`
Get current routing configuration.

**Response:**
```json
{
  "allowed_personas": ["generalist", "researcher"],
  "enable_adaptive_routing": true
}
```

### PUT `/api/v1/management/config/routing`
Update routing configuration.

**Request:**
```json
{
  "allowed_personas": ["generalist", "researcher", "coder"],
  "enable_adaptive_routing": true
}
```

### GET `/api/v1/management/backends`
List all configured backends with status.

**Response:**
```json
{
  "backends": [
    {
      "name": "ollama",
      "type": "ollama",
      "is_available": true,
      "last_checked": 1702648475.123,
      "config": {}
    }
  ]
}
```

### POST `/api/v1/management/backends/{name}/test`
Test connectivity of a specific backend.

**Response:**
```json
{
  "success": true,
  "latency_ms": 45.2,
  "error": null
}
```

### GET `/api/v1/management/context/config`
Get context pipeline configuration.

**Response:**
```json
{
  "extra_documents_dir": null,
  "enable_semantic_chunking": true,
  "max_combined_context_tokens": 8192
}
```

### PUT `/api/v1/management/config/context`
Update context pipeline configuration.

**Request:**
```json
{
  "extra_documents_dir": "/path/to/docs",
  "enable_semantic_chunking": true,
  "max_combined_context_tokens": 16384
}
```

### GET `/api/v1/management/security/status`
Get security configuration status.

**Response:**
```json
{
  "api_keys_count": 2,
  "audit_log_enabled": true
}
```

### POST `/api/v1/management/personas`
Create a new persona.

**Request:**
```json
{
  "name": "custom-persona",
  "description": "A custom persona for specific tasks",
  "system_prompt": "You are a helpful assistant specialized in...",
  "max_context_window": 4096,
  "routing_hint": "general"
}
```

**Response:**
```json
{
  "name": "custom-persona",
  "description": "A custom persona for specific tasks",
  "system_prompt": "You are a helpful assistant specialized in...",
  "max_context_window": 4096,
  "routing_hint": "general",
  "is_active": true
}
```

### PUT `/api/v1/management/personas/{name}`
Update an existing persona.

**Request:**
```json
{
  "description": "Updated description",
  "max_context_window": 8192
}
```

### DELETE `/api/v1/management/personas/{name}`
Delete a persona.

**Response:**
```json
{
  "message": "Persona 'custom-persona' deleted successfully"
}
```

### POST `/api/v1/management/config/save`
Save current configuration.

**Response:**
```json
{
  "success": true,
  "config_hash": "a1b2c3d4e5f6g7h8",
  "message": "Configuration saved successfully (in-memory only for now)"
}
```

---

## OpenAI-Compatible Endpoints

These endpoints provide drop-in compatibility with OpenAI API clients.

### POST `/v1/chat/completions`
OpenAI-compatible chat completions.

**Request:**
```json
{
  "model": "adaptivemind-default",
  "messages": [{"role": "user", "content": "Hello!"}],
  "temperature": 0.7,
  "max_tokens": 512,
  "stream": false
}
```

**Response:**
```json
{
  "id": "chatcmpl-1702648475",
  "object": "chat.completion",
  "created": 1702648475,
  "model": "ollama",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you today?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 15,
    "total_tokens": 25
  }
}
```

### GET `/v1/models`
List models in OpenAI-compatible format.

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "llama3.2:latest",
      "object": "model",
      "created": 1702648475,
      "owned_by": "adaptivemind"
    }
  ]
}
```

---

## Planned Endpoints (Not Yet Implemented)

The following endpoints are documented in the OpenAPI spec but not yet implemented:

- `/api/v1/chat/stream` - Streaming chat responses
- `/api/v1/agents/*` - Agent execution and management
- `/api/v1/memory/*` - Memory management
- `/api/v1/workflows/*` - Workflow execution
- `/api/v1/security/*` - Security validation and auditing
- `/api/v1/feed/ingest` - Content ingestion
- `/api/v1/jobs/*` - Async job processing

See `api_schemas/adaptive_swarm_models.yaml` for the Adaptive Swarm System API schemas (planned).
