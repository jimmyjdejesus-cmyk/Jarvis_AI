from v2.agent.adapters.langgraph_ui import WorkflowVisualizer


def test_team_indicators_and_dead_ends():
    viz = WorkflowVisualizer()
    viz.add_event({"id": "team1", "type": "Team", "label": "code_review", "color": "blue"})
    viz.add_event({"id": "analysis", "type": "ToolCall", "status": "pruned"})

    indicators = viz.get_team_indicators()
    assert indicators and indicators[0]["icon"] == "🧑\u200d💻"
    assert indicators[0]["label"] == "code_review"

    dead_ends = viz.get_dead_ends()
    assert dead_ends == ["analysis"]
