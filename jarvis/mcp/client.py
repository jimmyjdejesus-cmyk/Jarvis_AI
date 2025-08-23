"""MCP Client for Model Context Protocol communication"""

import asyncio
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

import aiohttp

from jarvis.security.decorators import rate_limit, timeout
from jarvis.homeostasis.monitor import SystemMonitor

logger = logging.getLogger(__name__)
ws7_logger = logging.getLogger("ws7")


class MCPError(Exception):
    """Base exception for MCP client"""


class MCPConnectionError(MCPError):
    """Raised when the client cannot reach a server"""


class MCPAPIError(MCPError):
    """Raised when an API returns an error response"""


class MCPClient:
    """Model Context Protocol client for multi-model communication"""

    def __init__(
        self, servers: Dict[str, str] | None = None, monitor: SystemMonitor | None = None
    ) -> None:
        """Initialize MCP client with server configurations."""

        self.servers = servers or {
            "ollama": "http://localhost:11434",
            "openai": "https://api.openai.com/v1",
            "anthropic": "https://api.anthropic.com/v1",
        }
        self.active_connections: Dict[str, str] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        self.monitor = monitor

    async def __aenter__(self) -> "MCPClient":
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.session:
            await self.session.close()

    async def _request_with_retry(
        self,
        method: str,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        json: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
        retries: int = 3,
        backoff: float = 2.0,
    ) -> Any:
        """Make an HTTP request with retry and exponential backoff."""

        assert self.session is not None, "Client session not initialized"
        for attempt in range(retries):
            try:
                async with self.session.request(
                    method, url, headers=headers, json=json, timeout=timeout
                ) as resp:
                    if resp.status >= 400:
                        text = await resp.text()
                        # Retry on transient HTTP errors
                        if resp.status == 429 or resp.status >= 500:
                            if attempt < retries - 1:
                                await asyncio.sleep(backoff ** attempt)
                                continue
                        raise MCPAPIError(f"HTTP {resp.status}: {text}")
                    if resp.content_type == "application/json":
                        return await resp.json()
                    return await resp.text()
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt == retries - 1:
                    raise MCPConnectionError(str(e)) from e
                await asyncio.sleep(backoff ** attempt)

    async def check_server_health(self, server_name: str) -> bool:
        """Check if a server is reachable and healthy."""

        if server_name not in self.servers:
            return False
        base = self.servers[server_name]

        try:
            if server_name == "ollama":
                await self._request_with_retry("GET", f"{base}/api/tags", timeout=5)
            elif server_name == "openai":
                key = os.getenv("OPENAI_API_KEY")
                if not key:
                    return False
                await self._request_with_retry(
                    "GET",
                    f"{base}/models",
                    headers={"Authorization": f"Bearer {key}"},
                    timeout=5,
                )
            elif server_name == "anthropic":
                key = os.getenv("ANTHROPIC_API_KEY")
                if not key:
                    return False
                await self._request_with_retry(
                    "GET",
                    f"{base}/models",
                    headers={
                        "x-api-key": key,
                        "anthropic-version": "2023-06-01",
                    },
                    timeout=5,
                )
            else:
                await self._request_with_retry("GET", base, timeout=5)
            return True
        except MCPError:
            return False

    async def connect_to_server(self, server_name: str) -> bool:
        """Establish connection to MCP server."""

        if server_name not in self.servers:
            logger.error("Unknown server: %s", server_name)
            return False

        healthy = await self.check_server_health(server_name)
        if healthy:
            self.active_connections[server_name] = self.servers[server_name]
            logger.info("Connected to %s", server_name)
            return True
        logger.error("Failed to connect to %s", server_name)
        return False
    @rate_limit(calls=10, period=60)
    @timeout(10)
    async def list_models(self, server_name: str) -> List[str]:
        """Get available models from server."""

        if server_name not in self.active_connections:
            if not await self.connect_to_server(server_name):
                return []

        try:
            if server_name == "ollama":
                data = await self._request_with_retry(
                    "GET", f"{self.servers[server_name]}/api/tags"
                )
                return [model["name"] for model in data.get("models", [])]
            elif server_name == "openai":
                key = os.getenv("OPENAI_API_KEY")
                data = await self._request_with_retry(
                    "GET",
                    f"{self.servers[server_name]}/models",
                    headers={"Authorization": f"Bearer {key}"},
                )
                return [m["id"] for m in data.get("data", [])]
            elif server_name == "anthropic":
                # Anthropic does not provide a public model list endpoint; return common models
                return ["claude-3.5-sonnet", "claude-3"]
        except MCPError as e:
            logger.error("Failed to list models for %s: %s", server_name, e)

        return []

    def _emit_llm_call(
        self,
        server: str,
        model: str,
        success: bool,
        duration: float,
        error: Optional[str] = None,
    ) -> None:
        """Emit telemetry event for an LLM call."""

        ws7_logger.info(
            "Metrics.LLMCall",
            extra={
                "server": server,
                "model": model,
                "success": success,
                "duration_ms": int(duration * 1000),
                "error": error,
            },
        )

    @rate_limit(calls=5, period=60)
    @timeout(30)
    async def generate_response(self, server: str, model: str, prompt: str) -> str:
        """Generate response using specific model via MCP."""

        if server not in self.active_connections:
            if not await self.connect_to_server(server):
                raise MCPConnectionError(f"Cannot connect to server: {server}")

        start = time.perf_counter()
        try:
            if server == "ollama":
                result = await self._generate_ollama_response(model, prompt)
            elif server == "openai":
                result = await self._generate_openai_response(model, prompt)
            elif server == "anthropic":
                result = await self._generate_anthropic_response(model, prompt)
            else:
                raise MCPError(f"Unsupported server: {server}")

            if self.monitor:
                self.monitor.record_tokens(len(prompt) + len(result))
            self._emit_llm_call(server, model, True, time.perf_counter() - start)
            return result
        except MCPError as e:
            self._emit_llm_call(
                server, model, False, time.perf_counter() - start, str(e)
            )
            raise

    async def _generate_ollama_response(self, model: str, prompt: str) -> str:
        """Generate response using Ollama API."""

        payload = {"model": model, "prompt": prompt, "stream": False}
        data = await self._request_with_retry(
            "POST", f"{self.servers['ollama']}/api/generate", json=payload
        )
        return data.get("response", "No response received")

    async def _generate_openai_response(self, model: str, prompt: str) -> str:
        """Generate response using OpenAI API."""

        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise MCPConnectionError("OPENAI_API_KEY not set")
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        }
        data = await self._request_with_retry(
            "POST", f"{self.servers['openai']}/chat/completions", headers=headers, json=payload
        )
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            raise MCPAPIError(f"Unexpected OpenAI response: {data}") from e

    async def _generate_anthropic_response(self, model: str, prompt: str) -> str:
        """Generate response using Anthropic API."""

        key = os.getenv("ANTHROPIC_API_KEY")
        if not key:
            raise MCPConnectionError("ANTHROPIC_API_KEY not set")
        headers = {
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": model,
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
        }
        data = await self._request_with_retry(
            "POST", f"{self.servers['anthropic']}/messages", headers=headers, json=payload
        )
        try:
            return data["content"][0]["text"]
        except (KeyError, IndexError) as e:
            raise MCPAPIError(f"Unexpected Anthropic response: {data}") from e

    def get_connected_servers(self) -> List[str]:
        """Get list of currently connected servers."""

        return list(self.active_connections.keys())

    def get_server_status(self) -> Dict[str, Any]:
        """Get status of all configured servers."""

        status: Dict[str, Any] = {}
        for server_name, server_url in self.servers.items():
            status[server_name] = {
                "url": server_url,
                "connected": server_name in self.active_connections,
                "last_check": None,
            }
        return status

    # ------------------------------------------------------------------
    @rate_limit(calls=10, period=60)
    @timeout(30)
    async def execute_tool(
        self, server: str, tool: str, params: Dict[str, Any] | None = None
    ) -> Any:
        """Execute a tool exposed by an MCP server.

        The default implementation expects servers to expose tool endpoints at
        ``/tools/{tool}`` and to accept JSON payloads.  This lightweight
        wrapper enables end-to-end testing with mock servers and can be
        extended for specific server behaviours.
        """

        if server not in self.active_connections:
            if not await self.connect_to_server(server):
                raise MCPConnectionError(f"Cannot connect to server: {server}")

        base = self.servers[server].rstrip("/")
        return await self._request_with_retry(
            "POST", f"{base}/tools/{tool}", json=params or {}
        )
