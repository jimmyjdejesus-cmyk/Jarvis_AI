# ui/main_window.py
import tkinter as tk
from tkinter import ttk
from threading import Thread
from orchestrator import Orchestrator
from tools.autotune import find_optimal_threshold
from ui.components.chat_panel.app import ChatPanel
from ui.components.settings_panel.settings_panel import SettingsPanel
from ui.components.log_viewer.log_viewer import LogViewerWindow
import settings

class MainWindow(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        # Load saved model if exists
        try:
            with open("active_model.cfg", "r") as f:
                saved_model = f.read().strip()
                if saved_model in settings.AVAILABLE_MODELS:
                    settings.ACTIVE_MODEL_NAME = saved_model
        except FileNotFoundError:
            pass
        self.orchestrator = Orchestrator()

        paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned_window.pack(fill="both", expand=True, padx=10, pady=10)

        # Initialize and add the settings panel, passing its callbacks
        self.settings_panel = SettingsPanel(
            paned_window, 
            autotune_callback=self.start_autotune,
            log_viewer_callback=self.open_log_viewer,
            save_model_callback=self.save_model_choice
        )
        paned_window.add(self.settings_panel, weight=1)

        # Initialize and add the chat panel
        self.chat_panel = ChatPanel(paned_window, send_callback=self.handle_send_message)
        paned_window.add(self.chat_panel, weight=3)

        self.chat_panel.add_message(f"J.A.R.V.I.S.: Online. Model: {settings.ACTIVE_MODEL_NAME}")

    def handle_send_message(self, user_input):
        self.chat_panel.add_message(f"You: {user_input}")
        self.chat_panel.toggle_input(enabled=False)
        thread = Thread(target=self.get_agent_response, args=(user_input,))
        thread.start()

    def get_agent_response(self, user_input):
        response_text, tokens_used = self.orchestrator.handle_request(user_input)
        self.add_message_to_chat(f"J.A.R.V.I.S.: {response_text} (Tokens: {tokens_used})")
        self.chat_panel.toggle_input(enabled=True)

    def start_autotune(self):
        self.add_message_to_chat("J.A.R.V.I.S.: Starting auto-tuner...")
        # Note: This uses a placeholder function. You'll need to create find_optimal_threshold
        # or adapt the logic from your tools/autotune.py
        thread = Thread(target=find_optimal_threshold, args=(self.add_message_to_chat,))
        thread.start()

    def open_log_viewer(self):
        if not hasattr(self, "log_window") or not self.log_window.winfo_exists():
            self.log_window = LogViewerWindow(self.master)
        else:
            self.log_window.lift()

    def save_model_choice(self, model_name):
        """Saves the selected model name to a file for the next session."""
        settings.ACTIVE_MODEL_NAME = model_name  # Update in-memory setting
        with open("active_model.cfg", "w") as f:
            f.write(model_name)
        self.add_message_to_chat(f"Model selection saved to '{model_name}'. Please restart the application to apply.")

    def add_message_to_chat(self, message):
        self.master.after(0, self.chat_panel.add_message, message)