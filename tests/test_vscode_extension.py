import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from integrations.vscode.extension import debug_error, explain_code_selection


class DummyAgent:
    def debug_assistance(self, error_message, code, language):
        return "dummy help"

    def explain_code(self, code, language):
        return "dummy explanation"


def _patch_agent(monkeypatch):
    monkeypatch.setattr(
        "integrations.vscode.extension._get_coding_agent", lambda workspace=None: DummyAgent()
    )


def test_explain_code_suggestions(tmp_path, monkeypatch):
    file = tmp_path / "sample.py"
    file.write_text("def foo():\n    pass\n")
    _patch_agent(monkeypatch)

    result = explain_code_selection("foo()", workspace=str(tmp_path))
    assert result["success"]
    assert any("sample.py" in r["path"] for r in result["suggestions"])


def test_debug_error_related_files(tmp_path, monkeypatch):
    file = tmp_path / "main.py"
    file.write_text("raise ValueError('boom')\n# ValueError\n")
    _patch_agent(monkeypatch)

    result = debug_error("ValueError", workspace=str(tmp_path))
    assert result["success"]
    assert any("main.py" in r["path"] for r in result["related_files"])
