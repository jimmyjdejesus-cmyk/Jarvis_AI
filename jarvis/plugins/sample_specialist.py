"""Example specialist plugin."""
from jarvis_sdk import jarvis_plugin
import ast


@jarvis_plugin(plugin_type="specialist", description="Evaluate a math expression")
class MathSpecialist:
    """Evaluate math expressions using ``ast.literal_eval``."""

    def run(self, expression: str) -> str:
        """Return the evaluated result of ``expression``."""
        return str(ast.literal_eval(expression))
