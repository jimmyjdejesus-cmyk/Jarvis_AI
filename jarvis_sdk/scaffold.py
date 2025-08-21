"""Utilities for scaffolding new plugins."""
from pathlib import Path

PLUGIN_TEMPLATE = '''from jarvis_sdk import jarvis_plugin

@jarvis_plugin(plugin_type="{plugin_type}", description="{description}")
def {name}():
    """{description}"""
    # TODO: implement plugin logic
    return None
'''


def create_plugin(directory: str, name: str, *, plugin_type: str = "tool", description: str = "Sample plugin") -> Path:
    """Create a basic plugin module in the given directory."""
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    file_path = path / f"{name}.py"
    file_path.write_text(PLUGIN_TEMPLATE.format(name=name, plugin_type=plugin_type, description=description))
    return file_path
