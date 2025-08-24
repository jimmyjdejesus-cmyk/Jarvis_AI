import sys
from pathlib import Path
from unittest.mock import patch

# Ensure legacy package is importable
sys.path.append(str(Path(__file__).parent.parent))

from agent.tools import run_tool


def test_open_file_dispatch():
    """IDE open_file command triggers integration with confirmation."""
    with patch('agent.tools.JetBrainsIntegration') as MockIDE, \
         patch('builtins.input', return_value='y'):
        instance = MockIDE.return_value
        instance.open_file.return_value = {"success": True}

        result = run_tool({
            'tool': 'ide_command',
            'args': {
                'command': 'open_file',
                'file_path': 'example.py'
            }
        })

        instance.open_file.assert_called_once_with('example.py', None)
        assert result == {"success": True}


def test_run_lint_dispatch():
    """IDE run_lint command invokes run_ide_command with inspect."""
    with patch('agent.tools.JetBrainsIntegration') as MockIDE, \
         patch('builtins.input', return_value='y'):
        instance = MockIDE.return_value
        instance.run_ide_command.return_value = {"returncode": 0}

        result = run_tool({
            'tool': 'ide_command',
            'args': {
                'command': 'run_lint',
                'target': 'example.py'
            }
        })

        instance.run_ide_command.assert_called_once_with('inspect', ['example.py'])
        assert result == {"returncode": 0}
