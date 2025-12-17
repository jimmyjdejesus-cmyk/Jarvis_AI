
Copyright (c) 2025 Jimmy De Jesus (Bravetto)

Licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0).
See https://creativecommons.org/licenses/by/4.0/ for license terms.

# Python SDK Guide

The Python SDK wraps the AdaptiveMind AI v1 API with convenient methods and API key handling.

## Install
```bash
pip install -e ./sdk/python
```

## Configure
- API base URL (default: `http://127.0.0.1:8000`)
- API Key via `ADAPTIVEMIND_API_KEY` env var or `api_key` argument

## Examples
```python
from jarvis_sdk import JarvisClient

client = JarvisClient(api_key="YOUR_API_KEY")
print(client.health())
print(client.models())

# Chat
resp = client.chat(messages=[{"role": "user", "content": "Write a haiku about code"}], temperature=0.7)
print(resp["content"])

# Streaming chat
for chunk in client.chat_stream(messages=[{"role": "user", "content": "Stream reply"}]):
    print(chunk, end="")

# Feed ingest
client.feed_ingest([
    {"source": "web", "content": "New document content", "metadata": {"subject": "doc"}}
])

# Async job
job = client.jobs_submit(mode="chat", payload={"messages": [{"role": "user", "content": "via job"}]})
status = client.jobs_submit_and_wait("chat", {"messages": [{"role": "user", "content": "via job"}]})
print(status)
```

## Methods
- Health/Models: `health`, `models`
- Chat: `chat`, `chat_stream`
- Agents: `agents`, `agent_execute`, `agents_collaborate`, `agent_capabilities`
- Memory/Feed: `memory_stats`, `feed_ingest`
- Workflows: `workflow_execute`, `workflow_capabilities`, `workflows_active`
- Jobs: `jobs_submit`, `job_status`, `jobs_submit_and_wait`
- Security: `security_validate`, `security_events`, `security_stats`, `security_audit`
- Monitoring: `monitoring_metrics`, `monitoring_summary`, `monitoring_health`,
  `monitoring_performance`, `monitoring_export`
