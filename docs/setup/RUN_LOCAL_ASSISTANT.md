
Copyright (c) 2025 Jimmy De Jesus (Bravetto)

Licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0).
See https://creativecommons.org/licenses/by/4.0/ for license terms.

Run Local Assistant (Quickstart)

Follow these steps to get a local assistant up and running quickly using the modern Jarvis runtime
(recommended). This guide assumes you have Ollama installed as the local model provider.

Note: The legacy runtime has been archived to `archive/legacy`. If you need the legacy runtime
for migration or testing, follow the restoration instructions below.

1) Install Ollama and fetch a local model

```bash
# Homebrew (macOS)
brew install ollama
ollama pull llama3.2:3b
```

2) Install Python dependencies (use a venv, for example, conda or python -m venv)

```bash
# From the repository root
pip install -r requirements.txt
# Optionally install dev requirements
pip install -r requirements-dev.txt
```

3) Start the local server

```bash
# The legacy runtime has been archived to `archive/legacy` as part of the repository cleanup.
# To run the modern Jarvis runtime instead (recommended), start:
uvicorn jarvis_core.server:build_app --factory --host 127.0.0.1 --port 8000

# If you explicitly need to run the legacy runtime, restore it first:
# git mv archive/legacy legacy && uvicorn legacy.app.main:app --reload --port 8000
```

4) Test the chat endpoint

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "What is Python?"}]}'
```

Expected: 200 OK with a JSON response containing the assistant reply.
If the endpoint returns 503, ensure `ollama` is running and a model is pulled.

Notes
* Uses `MCPJarvisAgent` with `force_local=True` to prefer local models.
* If your `ollama` binary requires a non-default host/port, set `OLLAMA_HOST` in the environment.
