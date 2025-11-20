Run Local Assistant (Quickstart)

Follow these steps to get a local assistant up and running ASAP using Jarvis legacy runtime and Ollama as a local model provider.

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
# Run legacy app (runs API with /api/v1/* endpoints)
uvicorn legacy.app.main:app --reload --port 8000
```

4) Test the local-only endpoint

```bash
curl -X POST http://localhost:8000/api/v1/local_chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "What is Python?"}] }'
```

Expected: 200 OK with a JSON response containing the assistant reply. If the endpoint returns 503, ensure `ollama` is running and a model is pulled.

Notes
* This uses `MCPJarvisAgent` with `force_local=True` so only local models are used.
* If your `ollama` binary or service requires different host/port, set `OLLAMA_HOST` in the environment or in `legacy/.env`.
