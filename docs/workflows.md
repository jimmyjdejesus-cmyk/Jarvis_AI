# Pre-made LangGraph Workflows

Jarvis AI ships with a small library of reusable workflow templates built on **LangGraph**. These examples demonstrate common patterns that developers can adapt for their own automation tasks.

## Available Workflows

- **Data Analysis Workflow** – loads a dataset, performs analysis and returns insights.
- **Research & Summarization Workflow** – gathers information from multiple sources and synthesizes a report.
- **Code Review Workflow** – runs static analysis and tests before producing a review summary.
- **API Integration Workflow** – fetches data from multiple endpoints with basic error handling.

To explore the templates, run:

```bash
python custom_workflows/workflow_templates.py
```

Each workflow class can be subclassed or used as-is to accelerate development of LangGraph-based agents.
