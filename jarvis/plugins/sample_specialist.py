"""Example specialist plugin."""
from jarvis_sdk import jarvis_plugin


@jarvis_plugin(plugin_type="specialist", description="Evaluate a math expression")
class MathSpecialist:
    def run(self, expression: str) -> str:
import ast

@jarvis_plugin(plugin_type="specialist", description="Evaluate a math expression")
class MathSpecialist:
    def run(self, expression: str) -> str:
        return str(ast.literal_eval(expression))
