
Copyright (c) 2025 Jimmy De Jesus (Bravetto)

Licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0).
See https://creativecommons.org/licenses/by/4.0/ for license terms.

# Local Assistant Runtime Guide

This guide documents the new Jarvis local runtime with emphasis on deep
research workflows, routing strategies, and observability.

## Architecture Highlights

- **AdaptiveMindApplication** wires configuration, context engineering, monitoring, and LLM backends.
- **AdaptiveLLMRouter** picks the best backend for each persona, trying
  Ollama, then WindowsML (when available), and finally the deterministic
  contextual fallback.
- **ContextEngine** assembles persona prompts, conversation history, research
  snippets, and optional `.txt` documents from
  `context_pipeline.extra_documents_dir`.
- **MetricsRegistry** and **TraceCollector** capture latency, token usage,
  personas, and backend selections for later harvesting.

## Deep Research Workflow

1. Define a persona with a research-focused system prompt in the configuration.
2. Enable `enable_research_features` and provide an `extra_documents_dir` with curated notes.
3. Submit chat requests with `metadata.objective` to label traces.
  The router stores them for subsequent analysis via
  `/api/v1/monitoring/traces`.
4. Review `/api/v1/monitoring/metrics` to monitor latency, token counts, and context usage.

## WindowsML Acceleration

On Windows, provide an ONNX model through configuration:

```json
{
  "windowsml": {
    "enabled": true,
    "model_path": "C:/models/jarvis-response.onnx",
    "device_preference": "dml"
  }
}
```

When the DirectML provider is available, the backend accelerates
inference. If the runtime cannot initialise WindowsML, the router
automatically proceeds to the contextual fallback and logs the degraded
mode.

## API Keys and Cloud Usage

To gate cloud-based workflows, set API keys in configuration or the
`ADAPTIVEMIND_API_KEYS` environment variable. The server requires `X-API-Key`
(or `api_key` query parameter) for every authenticated request. Failed
attempts are rejected with HTTP 401 and logged by the central logger for
auditing.

## Extending with MCP/LSP Templates

The `jarvis_core/extensions/templates.py` module contains templates for:

- **MCP (Model Context Protocol)** – define servers and capabilities for context streaming.
- **LSP (Language Server Protocol)** – describe command invocations for IDE-grade assistance.

Each template exposes a simple `entrypoint` callable and a configuration
schema to bootstrap integrations without editing core routing code.

## Observability Playbook

1. Configure log output with `ADAPTIVEMIND_LOG_LEVEL=DEBUG` for detailed traces.
2. Poll `/api/v1/monitoring/metrics` regularly to harvest aggregated metrics.
3. Use `/api/v1/monitoring/traces` to trace persona-specific behaviour and backend choices.
4. Optionally persist audit logs by pointing `security.audit_log_path` to a file location.

## Testing

`pytest` runs both unit and integration tests.

Integration tests spin up the FastAPI application and perform
persona-aware chats. They validate metrics/traces and exercise API-key
enforcement to prevent regression drift.

## Maintenance Checklist

- Update persona definitions in configuration as new workflows are introduced.
- Ensure ONNX models are validated before enabling WindowsML acceleration.
- Monitor the metrics harvest logs for unusual latency spikes.
- Extend MCP/LSP templates when integrating additional protocols or tools.
