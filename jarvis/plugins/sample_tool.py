"""Example tool plugin."""
from jarvis_sdk import jarvis_plugin


@jarvis_plugin(plugin_type="tool", description="Say hello to a user")
def greet(name: str = "world") -> str:
    """Return a friendly greeting addressed to ``name``."""
    return f"Hello {name}!"
