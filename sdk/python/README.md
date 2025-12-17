
Copyright (c) 2025 Jimmy De Jesus (Bravetto)

Licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0).
See https://creativecommons.org/licenses/by/4.0/ for license terms.

# AdaptiveMind AI Python SDK

A lightweight SDK to integrate with the AdaptiveMind AI v1 API.

## Install

```bash
pip install -e ./sdk/python
```

## Quickstart

```python
from jarvis_sdk import JarvisClient

client = JarvisClient(base_url="http://127.0.0.1:8000", api_key="YOUR_API_KEY")
print(client.health())
print(client.models())

# Chat
resp = client.chat(messages=[{"role": "user", "content": "Hello"}])
print(resp)

# Feed ingest
client.feed_ingest([
    {"source": "docs", "content": "New update", "metadata": {"subject": "release"}}
])

# Jobs (async)
job = client.jobs_submit("chat", {"messages": [{"role": "user", "content": "run via job"}]})
status = client.job_status(job["job_id"])
print(status)
```

## Auth
- Set `X-API-Key` header via `api_key` or `ADAPTIVEMIND_API_KEY` env var.

## Endpoints covered
- Health, Models, Chat (streaming and non-streaming)
- Agents (execute, collaborate, capabilities)
- Memory (stats), Feed ingestion
- Workflows (execute, capabilities, active)
- Jobs (submit, status)
- Security (validate, events, stats, audit)
- Monitoring (metrics, summary, health, performance, export)
