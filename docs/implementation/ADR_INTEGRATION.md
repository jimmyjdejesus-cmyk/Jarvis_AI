# Integrating Auto-Deep-Research (ADR) into Jarvis_AI

This document outlines how to integrate Auto-Deep-Research (ADR) as an optional provider in Jarvis_AI while keeping separation of concerns.

## Goals
- Add ADR as an optional local provider for research tasks.
- Minimal changes to existing components: MCPClient, ModelRouter, ResearchAgent.
- Keep ADR pluggable (submodule or HTTP) with health checks and fallbacks.

## Recommended Approach (Blackbox HTTP Provider)
1. Add `ADR_BASE_URL` env variable and optional `ENABLE_ADR`.
2. Add a small adapter at `legacy/jarvis/integrations/auto_deep_research/bridge.py` that wraps ADR HTTP API: `generate`, `health_check`.
3. Update `legacy/jarvis/mcp/client.py` to support `adr` server: add to `self.servers` and add private method `_generate_adr_response` that uses `self._request_with_retry` to `ADR_BASE_URL/api/generate` and returns text.
4. Add `auto-deep-research` ModelMetadata in `ModelRouter` with strengths `['research','web_research','document_analysis']`.
5. Update `legacy/jarvis/agents/research_agent.py` to prefer `task_type='research'` when routing to `ModelRouter`, and optionally use `force_local` when ADR is enabled.
6. Tests: Add unit tests and a small integration test in `tests/` that mocks ADR HTTP endpoints.

## Alternative: Submodule + Direct Import
If you want ADR available as a Python package and not as an HTTP service, add it as a submodule and wrap a local API call or use ADR code directly via the adapter. However, keep the same optional behavior.

## Deployment & Maintenance
- Keep ADR as an optional submodule or service; never require it for Jarvis core to start.
- Use `ENABLE_ADR` to switch on/off, `ADR_BASE_URL` to point to the ADR HTTP server.

## Follow-up
- Create feature branch `feature/integrate-adr` and split the work across small PRs:
  - PR 1: Add adapter skeleton
  - PR 2: Add ADR in MCPClient
  - PR 3: Add ModelMetadata and research_agent changes
  - PR 4: Tests & docs
