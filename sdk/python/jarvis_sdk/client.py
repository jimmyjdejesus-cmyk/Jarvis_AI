# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



import os
import json
import time
import typing as t
import requests


class JarvisClient:
    """AdaptiveMind AI Python SDK client for the versioned `/api/v1` endpoints.

    Features:
    - API key authentication via `X-API-Key` header
    - Simple, typed methods for common operations (chat, feed ingestion, jobs, etc.)
    - Sensible defaults for local development

    Example:
        from jarvis_sdk.client import JarvisClient
        client = JarvisClient(base_url="http://127.0.0.1:8000", api_key="YOUR_KEY")
        health = client.health()
        models = client.models()
        chat = client.chat(messages=[{"role": "user", "content": "Hello"}])
    """

    def __init__(self, base_url: str | None = None, api_key: str | None = None, timeout: int = 30):
        self.base_url = (base_url or os.getenv("ADAPTIVEMIND_TEST_BASE_URL") or "http://127.0.0.1:8000").rstrip("/")
        self.api_key = api_key or os.getenv("ADAPTIVEMIND_API_KEY")
        self.timeout = timeout

        self._session = requests.Session()
        if self.api_key:
            self._session.headers.update({"X-API-Key": self.api_key})
        self._session.headers.update({"Content-Type": "application/json"})

    # -------------------- Core helpers --------------------
    def _url(self, path: str) -> str:
        return f"{self.base_url}/api/v1{path}"

    def _get(self, path: str, params: dict | None = None) -> requests.Response:
        return self._session.get(self._url(path), params=params, timeout=self.timeout)

    def _post(self, path: str, payload: dict | None = None, stream: bool = False) -> requests.Response:
        data = json.dumps(payload or {})
        return self._session.post(self._url(path), data=data, timeout=self.timeout, stream=stream)

    # -------------------- Health & Models --------------------
    def health(self) -> dict:
        """Get system health status."""
        r = self._get("/health")
        r.raise_for_status()
        return r.json()

    def models(self) -> list[str]:
        """List available LLM models."""
        r = self._get("/models")
        r.raise_for_status()
        return (r.json() or {}).get("models", [])

    # -------------------- Chat --------------------
    def chat(self, messages: list[dict], model: str | None = None, temperature: float | None = None, max_tokens: int | None = None) -> dict:
        """Send a non-streaming chat request.

        Args:
            messages: List of {"role": "user|system|assistant", "content": str}
            model: Optional model override
            temperature: Sampling temperature
            max_tokens: Max tokens to predict
        Returns:
            {"content": str, "model": str | None}
        """
        payload: dict[str, t.Any] = {"messages": messages}
        if model is not None:
            payload["model"] = model
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        r = self._post("/chat", payload)
        r.raise_for_status()
        return r.json()

    def chat_stream(self, messages: list[dict], model: str | None = None, temperature: float | None = None, max_tokens: int | None = None) -> t.Iterator[str]:
        """Streaming chat generator yielding text chunks."""
        payload: dict[str, t.Any] = {"messages": messages}
        if model is not None:
            payload["model"] = model
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        r = self._post("/chat/stream", payload, stream=True)
        r.raise_for_status()
        for line in r.iter_lines():
            if line:
                yield line.decode("utf-8", errors="ignore")

    # -------------------- Agents --------------------
    def agents(self) -> dict:
        """List available agents and count."""
        r = self._get("/agents")
        r.raise_for_status()
        return r.json()

    def agent_execute(self, agent_type: str, objective: str, context: dict | None = None, priority: int = 1, timeout: int = 300) -> dict:
        """Execute a task via a specific agent type."""
        payload = {
            "agent_type": agent_type,
            "objective": objective,
            "context": context or {},
            "priority": priority,
            "timeout": timeout,
        }
        r = self._post("/agents/execute", payload)
        r.raise_for_status()
        return r.json()

    def agents_collaborate(self, agent_types: list[str], objective: str, context: dict | None = None) -> dict:
        """Execute a collaboration between agents."""
        payload = {
            "agent_types": agent_types,
            "objective": objective,
            "context": context or {},
        }
        r = self._post("/agents/collaborate", payload)
        r.raise_for_status()
        return r.json()

    def agent_capabilities(self, agent_type: str) -> dict:
        """Get capabilities of a specific agent type."""
        r = self._get(f"/agents/capabilities/{agent_type}")
        r.raise_for_status()
        return r.json()

    # -------------------- Memory --------------------
    def memory_stats(self) -> dict:
        r = self._get("/memory/stats")
        r.raise_for_status()
        return r.json()

    def feed_ingest(self, items: list[dict], persist_to_knowledge: bool = True, persist_to_memory: bool = True) -> dict:
        """Ingest feed items into memory/knowledge graph."""
        payload = {
            "items": items,
            "persist_to_knowledge": persist_to_knowledge,
            "persist_to_memory": persist_to_memory,
        }
        r = self._post("/feed/ingest", payload)
        r.raise_for_status()
        return r.json()

    # -------------------- Workflows --------------------
    def workflow_execute(self, workflow_type: str, parameters: dict | None = None, priority: int = 1, timeout: int = 600) -> dict:
        payload = {
            "workflow_type": workflow_type,
            "parameters": parameters or {},
            "priority": priority,
            "timeout": timeout,
        }
        r = self._post("/workflows/execute", payload)
        r.raise_for_status()
        return r.json()

    def workflow_capabilities(self) -> dict:
        r = self._get("/workflows/capabilities")
        r.raise_for_status()
        return r.json()

    def workflows_active(self) -> dict:
        r = self._get("/workflows/active")
        r.raise_for_status()
        return r.json()

    # -------------------- Jobs --------------------
    def jobs_submit(self, mode: str, payload: dict, callback_url: str | None = None) -> dict:
        """Submit an async job (chat|agent|workflow)."""
        req = {"mode": mode, "payload": payload}
        if callback_url:
            req["callback_url"] = callback_url
        r = self._post("/jobs", req)
        r.raise_for_status()
        return r.json()

    def job_status(self, job_id: str) -> dict:
        r = self._get(f"/jobs/{job_id}")
        r.raise_for_status()
        return r.json()

    def jobs_submit_and_wait(self, mode: str, payload: dict, poll_interval: float = 1.0, timeout_s: int = 60) -> dict:
        """Submit a job and wait for completion (simple poller)."""
        submit = self.jobs_submit(mode, payload)
        job_id = submit.get("job_id")
        deadline = time.time() + timeout_s
        while time.time() < deadline:
            status = self.job_status(job_id)
            if status.get("status") in ("completed", "failed"):
                return status
            time.sleep(poll_interval)
        raise TimeoutError("Job did not complete in time")

    # -------------------- Security --------------------
    def security_validate(self, agent_id: str, action: str, context: dict | None = None) -> dict:
        payload = {"agent_id": agent_id, "action": action, "context": context or {}}
        r = self._post("/security/validate", payload)
        r.raise_for_status()
        return r.json()

    def security_events(self, limit: int = 100) -> dict:
        r = self._get("/security/events", params={"limit": limit})
        r.raise_for_status()
        return r.json()

    def security_stats(self) -> dict:
        r = self._get("/security/stats")
        r.raise_for_status()
        return r.json()

    def security_audit(self) -> dict:
        r = self._post("/security/audit", {})
        r.raise_for_status()
        return r.json()

    # -------------------- Monitoring --------------------
    def monitoring_metrics(self) -> dict:
        r = self._get("/monitoring/metrics")
        r.raise_for_status()
        return r.json()

    def monitoring_summary(self, time_window_minutes: int = 60) -> dict:
        r = self._get("/monitoring/summary", params={"time_window_minutes": time_window_minutes})
        r.raise_for_status()
        return r.json()

    def monitoring_health(self) -> dict:
        r = self._get("/monitoring/health")
        r.raise_for_status()
        return r.json()

    def monitoring_performance(self) -> dict:
        r = self._get("/monitoring/performance")
        r.raise_for_status()
        return r.json()

    def monitoring_export(self, format: str = "json") -> dict:
        r = self._get("/monitoring/export", params={"format": format})
        r.raise_for_status()
        return r.json()
