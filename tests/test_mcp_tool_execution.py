import asyncio
import sys

import pytest
from aiohttp import web

sys.path.append('.')

from jarvis.mcp.client import MCPClient


async def echo_handler(request):
    data = await request.json()
    return web.json_response({"echo": data})


@pytest.mark.asyncio
async def test_execute_tool():
    app = web.Application()
    app.router.add_post("/tools/echo", echo_handler)
    # simple health endpoint for connection check
    app.router.add_get("/", lambda request: web.Response(text="ok"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "localhost", 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]
    url = f"http://localhost:{port}/"

    client = MCPClient({"dummy": url})
    async with client:
        result = await client.execute_tool("dummy", "echo", {"message": "hello"})
        assert result == {"echo": {"message": "hello"}}

    await runner.cleanup()
