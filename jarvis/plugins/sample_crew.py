"""Example crew plugin."""
from jarvis_sdk import jarvis_crew


@jarvis_crew(description="Simple crew that echoes input")
class EchoCrew:
    def run(self, text: str) -> str:
        return text
