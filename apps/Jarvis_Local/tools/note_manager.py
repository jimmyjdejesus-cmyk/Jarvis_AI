# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



# tools/note_manager.py
import os

NOTES_DIR = "notes"
if not os.path.exists(NOTES_DIR):
    os.makedirs(NOTES_DIR)

def save_note(filename: str, content: str) -> str:
    """Saves content to a note with the given filename."""
    try:
        with open(os.path.join(NOTES_DIR, filename), "w") as f:
            f.write(content)
        return f"Successfully saved note to {filename}."
    except Exception as e:
        return f"Error saving note: {e}"