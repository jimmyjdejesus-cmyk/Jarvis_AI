# Migration Parity Checklist

Mapping of legacy LangGraph features to their V2 equivalents.

| Legacy Feature & Location | V2 Equivalent | Status |
| --- | --- | --- |
| Planner node (`legacy/agent/adapters/langgraph_workflow.py`) | `_planner_node` in `v2/agent/workflow_nodes.py` | ✅ ported |
| Code writer node (`legacy/agent/adapters/langgraph_workflow.py`) | `_code_writer_node` in `v2/agent/workflow_nodes.py` | ✅ ported |
| Debugger node (`legacy/agent/adapters/langgraph_workflow.py`) | `_debugger_node` in `v2/agent/workflow_nodes.py` | ✅ ported |
| Tool executor node (`legacy/agent/adapters/langgraph_workflow.py`) | `_tool_executor_node` in `v2/agent/workflow_nodes.py` | ✅ ported |
| Critic node (`legacy/agent/adapters/langgraph_workflow.py`) | `_critic_node` in `v2/agent/workflow_nodes.py` | ✅ ported |
| LangGraph UI (`legacy/agent/adapters/langgraph_ui.py`) | `v2/agent/adapters/langgraph_ui.py` | ✅ reimplemented |
| LangGraph agent (`legacy/agent/core/langgraph_agent.py`) | `v2/agent/core/agent.py` | ✅ replaced |
| Legacy Streamlit app (`legacy/app.py`) | V2 agent-first architecture | ✅ deprecated |
