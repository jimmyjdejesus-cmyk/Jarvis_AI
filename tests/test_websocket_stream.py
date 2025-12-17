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
import pytest
import websocket

BASE_URL = os.getenv("ADAPTIVEMIND_TEST_BASE_URL", "http://127.0.0.1:8000").replace("http", "ws")


def test_websocket_ping_pong():
    ws = websocket.WebSocket()
    try:
        ws.connect(f"{BASE_URL}/ws/pytest_client", header={"X-API-Key": "your-secret-api-key-here"})
        ws.send(json.dumps({"type": "ping"}))
        msg = ws.recv()
        assert msg is not None
    finally:
        try:
            ws.close()
        except Exception:
            pass
