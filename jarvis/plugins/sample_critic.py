"""Example critic plugin."""
from jarvis_sdk import jarvis_critic


@jarvis_critic(description="Ensure text is below a length limit")
def length_checker(text: str, max_length: int = 100) -> str:
    if len(text) > max_length:
        return f"Text too long by {len(text) - max_length} characters."
    return "Text length OK."
