"""Integration tests for the real MCPClient."""

from __future__ import annotations

from typing import AsyncIterator

import asyncio
import pytest
from pytest import MonkeyPatch
from aiohttp import web
import sys
import types
from pathlib import Path

neo4j_stub = types.ModuleType("neo4j")
neo4j_stub.GraphDatabase = object
neo4j_stub.Driver = object
sys.modules.setdefault("neo4j", neo4j_stub)

root = Path(__file__).resolve().parents[1]
jarvis_stub = types.ModuleType("jarvis")
jarvis_stub.__path__ = [str(root / "jarvis")]
sys.modules.setdefault("jarvis", jarvis_stub)

from jarvis.mcp.client import MCPClient  # noqa: E402


async def _start_mock_server() -> AsyncIterator[tuple[web.AppRunner, int]]:
    """Start a mock MCP server providing model listing and a simple tool."""

    app = web.Application()

    async def tags(request: web.Request) -> web.Response:
        return web.json_response({"models": [{"name": "test-model"}]})

    async def echo(request: web.Request) -> web.Response:
        data = await request.json()
        return web.json_response(data)

    app.router.add_get("/api/tags", tags)
    app.router.add_post("/tools/echo", echo)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]
    try:
        yield runner, port
    finally:  # pragma: no cover - cleanup
        await runner.cleanup()


async def _start_error_server() -> AsyncIterator[tuple[web.AppRunner, int]]:
    """Start a server that returns errors for model listing."""

    app = web.Application()

    async def tags(request: web.Request) -> web.Response:
        return web.Response(status=500)

    app.router.add_get("/api/tags", tags)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]
    try:
        yield runner, port
    finally:  # pragma: no cover - cleanup
        await runner.cleanup()


async def _start_auth_server() -> AsyncIterator[tuple[web.AppRunner, int]]:
    """Start a server that requires authentication for model listing."""

    app = web.Application()

    async def tags(request: web.Request) -> web.Response:
        return web.Response(status=401)

    app.router.add_get("/api/tags", tags)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]
    try:
        yield runner, port
    finally:  # pragma: no cover - cleanup
        await runner.cleanup()


async def _start_timeout_server() -> AsyncIterator[tuple[web.AppRunner, int]]:
    """Start a server that delays responses to trigger client timeouts."""

    app = web.Application()

    async def tags(request: web.Request) -> web.Response:
        await asyncio.sleep(0.2)
        return web.json_response({"models": [{"name": "slow-model"}]})

    app.router.add_get("/api/tags", tags)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]
    try:
        yield runner, port
    finally:  # pragma: no cover - cleanup
        await runner.cleanup()


@pytest.mark.asyncio
async def test_mcp_client_lists_models() -> None:
    async for runner, port in _start_mock_server():
        client = MCPClient(servers={"ollama": f"http://127.0.0.1:{port}"})
        async with client:
            models = await client.list_models("ollama")
        assert "test-model" in models
        break


@pytest.mark.asyncio
async def test_mcp_client_handles_server_error() -> None:
    async for runner, port in _start_error_server():
        client = MCPClient(servers={"ollama": f"http://127.0.0.1:{port}"})
        async with client:
            models = await client.list_models("ollama")
        assert models == []
        break


@pytest.mark.asyncio
async def test_mcp_client_execute_tool() -> None:
    async for runner, port in _start_mock_server():
        client = MCPClient(servers={"ollama": f"http://127.0.0.1:{port}"})
        async with client:
            result = await client.execute_tool(
                "ollama", "echo", {"foo": "bar"}
            )
        assert result == {"foo": "bar"}
        break


@pytest.mark.asyncio
async def test_mcp_client_handles_auth_failure() -> None:
    async for runner, port in _start_auth_server():
        client = MCPClient(servers={"ollama": f"http://127.0.0.1:{port}"})
        async with client:
            models = await client.list_models("ollama")
        assert models == []
        break


@pytest.mark.asyncio
async def test_mcp_client_handles_timeout(monkeypatch: MonkeyPatch) -> None:
    async for runner, port in _start_timeout_server():
        client = MCPClient(servers={"ollama": f"http://127.0.0.1:{port}"})

        original = MCPClient._request_with_retry

        async def patched_request(self, method, url, **kwargs):
            kwargs.update({"timeout": 0.05, "retries": 1})
            return await original(self, method, url, **kwargs)

        monkeypatch.setattr(MCPClient, "_request_with_retry", patched_request)

        async with client:
            models = await client.list_models("ollama")
        assert models == []
        break
