"""Example crew plugin."""
from jarvis_sdk import jarvis_crew


@jarvis_crew(description="Simple crew that echoes input")
class EchoCrew:
    """Crew that returns any provided text unchanged."""

    def run(self, text: str) -> str:
        """Return the given text."""
        return text