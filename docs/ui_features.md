# Multi-Pane UI Features

This frontend delivers a multi-pane layout for interacting with J.A.R.V.I.S.:

- **Chat Pane** – real-time conversation over WebSockets.
- **Workflow Pane** – live DAG visualization that updates when the backend emits `workflow_update`.
- **Log Viewer** – streams `agent.md` entries via `log_update` events.
- **HITL Oracle** – displays human-in-the-loop prompts pushed over `hitl_update`.

## Building the Frontend

Run the build script from the repository root:

```bash
./scripts/build_ui.sh
```

The script installs dependencies, builds the React interface, and bundles the Tauri application.
