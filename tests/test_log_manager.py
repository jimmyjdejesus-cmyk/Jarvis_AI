from pathlib import Path
import os
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))
import agent.log_manager as lm


def test_team_log_scoped(tmp_path, monkeypatch):
    monkeypatch.setenv("JARVIS_AUTOCONFIRM", "1")
    # Redirect project log to temporary location
    project_log = tmp_path / "agent_project.md"
    monkeypatch.setattr(lm, "PROJECT_LOG", project_log)

    team_dir = tmp_path / "team"
    lm.append_team_log(team_dir, "team entry")
    lm.append_project_log("project entry")

    assert (team_dir / "agent_team.md").read_text().strip() == "- team entry"
    assert project_log.read_text().strip() == "- project entry"


def test_query_logs(tmp_path, monkeypatch):
    monkeypatch.setenv("JARVIS_AUTOCONFIRM", "1")
    project_log = tmp_path / "agent_project.md"
    project_log.write_text("- nothing\n")
    team_dir = tmp_path / "team"
    team_dir.mkdir()
    (team_dir / "agent_team.md").write_text("- strategy: try A\n")
    monkeypatch.setattr(lm, "PROJECT_LOG", project_log)

    results = lm.query_logs("strategy", team_dir)
    assert results
    assert any("strategy" in r["content"] for r in results)
    assert any(r["file"].endswith("agent_team.md") for r in results)
