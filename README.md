# Jarvis Local Assistant Runtime

Jarvis_AI is a local-first multi-persona assistant that prioritises verifiable truth, observability, and secure extensibility. The new runtime ships with a simple Ollama-ready UI, an adaptive routing pipeline, and a comprehensive monitoring stack to support deep research workflows without sacrificing privacy.

## Key Features

- **Ollama UI** – Minimal single-page interface for sending prompts to the adaptive router. Works with the contextual fallback when Ollama is unavailable.
- **Context Engineering Pipeline** – Automatic persona prompts, conversation history, research snippets, and optional local documents with semantic chunking.
- **Adaptive Routing** – Persona-aware router selects between Ollama, WindowsML, or the contextual fallback while recording metrics and traces.
- **Security Controls** – API key enforcement and structured audit logging hooks to keep cloud usage gated.
- **Observability** – Central JSON logger, rolling metrics registry, and trace harvesting endpoints.
- **Extensibility Templates** – Ready-made templates for Model Context Protocol (MCP) and Language Server Protocol (LSP) adapters.

## Getting Started

### Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

### Running the API & UI

```bash
uvicorn jarvis_core.server:build_app --factory --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000/ for the UI. The backend automatically attempts to use a local Ollama instance (`OLLAMA_HOST`) and falls back to the contextual generator when unavailable. To enable WindowsML acceleration, set `JARVIS_CONFIG` to a JSON file that provides the ONNX model path on Windows.

### Configuration

Configuration is provided via JSON files (`~/.jarvis/config.json` by default) or environment variables. Key options:

| Option | Description |
| ------ | ----------- |
| `ollama.host` | Base URL for the Ollama server |
| `ollama.model` | Default model name (`llama3` by default) |
| `security.api_keys` | List of allowed API keys |
| `personas` | Persona definitions with prompts and routing hints |
| `context_pipeline.extra_documents_dir` | Directory with additional `.txt` documents added to the context |
| `monitoring.enable_metrics_harvest` | Enables background harvesting of metrics |

### Logging & Monitoring

- Logs are emitted in structured JSON format through the central logger (`JARVIS_LOG_LEVEL` and `JARVIS_LOG_PATH` control verbosity and destination).
- Metrics and traces are exposed via REST endpoints:
  - `GET /api/v1/monitoring/metrics`
  - `GET /api/v1/monitoring/traces`

### Security & API Keys

Supply comma-separated API keys via `JARVIS_API_KEYS` or `security.api_keys` in the config. Requests must include the `X-API-Key` header (or `api_key` query parameter) when keys are configured.

### Extending with MCP/LSP

Use the templates in `jarvis_core/extensions/templates.py` as starting points for adding MCP or LSP bridges. Each template defines an entrypoint and schema to encourage consistent integrations.

### Running Tests

```bash
pytest
```

The integration tests spin up the FastAPI application with the adaptive routing pipeline and validate persona routing, metrics harvesting, and API-key enforcement.

## Legacy Components

The `legacy/` folder keeps the historical mission-planning system for reference. The new runtime operates independently but can be bridged using the documented architecture in `UNIFIED_ARCHITECTURE.md`.
