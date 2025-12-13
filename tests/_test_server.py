"""Lightweight test server used by websocket tests.

Starts a Uvicorn server hosting the default Jarvis app so websocket
integration tests can connect to ws://127.0.0.1:8000/ws/pytest_client.
"""
import os
import uvicorn
from jarvis_core.server import build_app
from jarvis_core.config import AppConfig, MonitoringConfig, PersonaConfig


def make_app():
    config = AppConfig(
        personas={
            "generalist": PersonaConfig(
                name="generalist",
                description="Test persona",
                system_prompt="You are a helpful assistant.",
            )
        },
        allowed_personas=["generalist"],
        monitoring=MonitoringConfig(enable_metrics_harvest=False, harvest_interval_s=60.0),
    )
    return build_app(config=config)


if __name__ == "__main__":
    # Add a lightweight testing websocket endpoint to support the websocket
    # integration tests which expect /ws/pytest_client to respond to ping.
    import json
    from fastapi import WebSocket

    app = make_app()

    @app.websocket("/ws/pytest_client")
    async def _pytest_ws(websocket: WebSocket):
        await websocket.accept()
        try:
            while True:
                msg_text = await websocket.receive_text()
                try:
                    msg = json.loads(msg_text)
                except Exception:
                    continue
                if msg.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
        except Exception:
            try:
                await websocket.close()
            except Exception:
                pass

    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
