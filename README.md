# J.A.R.V.I.S. — Local-first AI Runtime

Jarvis_AI is a local-first multi-persona assistant that prioritizes verifiable truth, observability, and secure extensibility. It integrates a modern runtime (`Jarvis_Local`) with a legacy compatibility layer so teams can migrate iteratively.

The architecture supports a central Meta-Agent that orchestrates multiple specialist LLMs, an adaptive routing pipeline, and a comprehensive monitoring stack to support research workflows while protecting privacy.

## Key Features

- **Agent-UI Integration** – Modern frontend interface for sending prompts to the adaptive router and viewing traces.
- **Context Engineering Pipeline** – Automatic persona prompts, conversation history, research snippets, and optional local documents with semantic chunking.
- **Adaptive Routing** – Persona-aware router selects between Ollama, WindowsML, or the contextual fallback while recording metrics and traces.
- **Security Controls** – API key enforcement and structured audit logging hooks to keep cloud usage gated.
- **Observability** – Central JSON logger, rolling metrics registry, and trace harvesting endpoints.
- **Extensibility Templates** – Templates for Model Context Protocol (MCP) and Language Server Protocol (LSP) adapters.

## Getting Started

### Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Running the API & UI

```bash
uvicorn jarvis_core.server:build_app --factory --host 127.0.0.1 --port 8000
```

The backend attempts to use a local Ollama instance (`OLLAMA_HOST`) and falls back to the contextual generator when unavailable.

## Running tests locally

- Install dev dependencies (recommended using a virtual environment):

```bash
# With UV package manager (recommended in this project)
uv sync --dev --all-extras --python $(which python)
```

- Run the test suite:

```bash
pytest -q
```

Test mode notes (for developers):

- Set `JARVIS_TEST_MODE=true` to enable test-only fallbacks used by the
	local test harness (e.g., relaxed CORS for websocket-client tests and a
	small fallback ExceptionMiddleware when Starlette's ExceptionMiddleware
	is not present). The test suite sets this automatically when running
	locally via `pytest` (see `tests/conftest.py`), but you can set it
	explicitly when debugging:

```bash
export JARVIS_TEST_MODE=true
pytest -q
```

Note: These test-only fallbacks are intentionally gated so production
deployments are not impacted. If you'd prefer not to use the fallbacks,
ensure a compatible Starlette/FastAPI version is installed (see
`requirements.txt`).

## Migration & Compatibility

This branch keeps the `legacy/` directory intact to preserve backwards compatibility and provides a `Jarvis_Local/` runtime that implements the newer architecture (modern agents, improved monitoring, and a simplified onboarding flow). Review the `docs/` folder for migration steps and API differences.

---

*Merged content from `origin/main` and `origin/dev` to present a single unified overview.*
