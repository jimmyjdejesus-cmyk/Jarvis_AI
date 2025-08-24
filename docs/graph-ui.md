# Graph UI

Jarvis can visualize agent workflows using a graph interface when the `orchestrator` extra is installed.
Launch the UI with:
```bash
pip install "jarvis-ai[orchestrator]"
jarvis graph
```

### Visual Indicators

The workflow graph uses simple color cues:

- **Green nodes** represent active teams.
- **Red nodes** mark pruned paths.
- **Dashed arrows** show lineage when one path is merged into another.
