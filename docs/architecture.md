# Architecture

## Event Schema

Jarvis emits structured events for observability and workflow visualisation. Each event is stored as a JSON object on its own line (JSONL) and contains the following fields:

- `timestamp` – ISO 8601 timestamp when the event occurred.
- `level` – log level (`debug`, `info`, `warning`, `error`).
- `message` – human readable description.
- `event_type` – optional category of the event.
- `correlation_id` – identifier used to group events belonging to the same workflow session.
- `data` – optional additional payload.

The formal specification is available as a JSON Schema at [`schemas/event.json`](../schemas/event.json).
