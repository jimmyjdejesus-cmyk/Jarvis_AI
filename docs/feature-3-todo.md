# Decision Trace Transparency Roadmap

To improve transparency and debugging:

- Add a UI view or log panel that exposes the full workflow graph, showing each tool invocation and specialist agent contribution.
- Integrate LangSmith to capture agent calls and tool usage with timestamps for later analysis.
- Mark pruned or merged paths explicitly, including sources for combined answers and rationale for abandoned branches.
- Provide a "show reasoning" toggle so users can reveal the steps and any branches taken or dropped.
- Surface currently backend-only graph and trace data through the user interface for easier auditing.

