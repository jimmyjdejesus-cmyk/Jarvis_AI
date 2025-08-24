"""
The Memory Bus Module
Handles the creation and management of the `agent.md` communication logs.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

class MemoryBus:
    """
    Manages the agent.md communication log for a specific directory.
    """
    def __init__(self, directory: str = "."):
        self.log_file = Path(directory) / "agent.md"
        self._initialize_log_file()

    def _initialize_log_file(self):
        """Create the log file with a header if it doesn't exist."""
        if not self.log_file.exists():
            # Ensure the parent directory exists before writing the file
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            header = (
                "# Jarvis AI - Agent Communication Log\n"
                "This file acts as a shared memory bus for all agent interactions in this directory.\n"
                "----------------------------------------------------------------------------------\n\n"
            )
            with open(self.log_file, "w", encoding="utf-8") as f:
                f.write(header)

    def log_interaction(self, agent_id: str, team: str, message: str, data: Dict[str, Any] = None):
        """
        Logs a structured message from an agent to the agent.md file.

        Args:
            agent_id (str): The unique identifier of the agent logging the message.
            team (str): The team the agent belongs to (e.g., 'Red', 'Blue', 'White').
            message (str): The primary message or action being logged.
            data (Dict[str, Any], optional): A dictionary for any additional structured data.
        """
        timestamp = datetime.utcnow().isoformat()
        
        log_entry = (
            f"## Agent Interaction\n"
            f"**Timestamp:** {timestamp}\n"
            f"**Agent ID:** {agent_id}\n"
            f"**Team:** {team}\n"
            f"**Action/Message:**\n"
            f"```\n"
            f"{message}\n"
            f"```\n"
        )

        if data:
            import json
            data_str = json.dumps(data, indent=2)
            log_entry += (
                f"**Associated Data:**\n"
                f"```json\n"
                f"{data_str}\n"
                f"```\n"
            )
        
        log_entry += "---\n\n"

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)

    def read_log(self) -> str:
        """Reads the entire content of the log file."""
        if self.log_file.exists():
            with open(self.log_file, "r", encoding="utf-8") as f:
                return f.read()
        return ""

# Example usage:
if __name__ == "__main__":
    # Create a bus for the current directory
    bus = MemoryBus()
    bus.log_interaction(
        agent_id="meta_agent_01",
        team="Meta",
        message="Initializing new orchestration for objective: 'Refactor the UI module'."
    )
    bus.log_interaction(
        agent_id="orchestrator_01",
        team="Orchestrator",
        message="Spawning teams to handle the refactoring task."
    )
    bus.log_interaction(
        agent_id="red_team_01",
        team="Red",
        message="Analyzing potential vulnerabilities in the current UI code.",
        data={"files_inspected": ["ui/gui.py"], "lines_of_code": 350}
    )
    print(f"Log created at: {bus.log_file.resolve()}")
