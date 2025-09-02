# ui/main_window.py
import tkinter as tk
from tkinter import ttk
from threading import Thread
from orchestrator import Orchestrator
from tools.autotune import find_optimal_threshold
from ui.components.chat_panel.app import ChatPanel
from ui.components.settings_panel.settings_panel import SettingsPanel

class MainWindow(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.orchestrator = Orchestrator()

        paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned_window.pack(fill="both", expand=True, padx=10, pady=10)

        self.settings_panel = SettingsPanel(paned_window, autotune_callback=self.start_autotune)
        paned_window.add(self.settings_panel, weight=1)

        self.chat_panel = ChatPanel(paned_window, send_callback=self.handle_send_message)
        paned_window.add(self.chat_panel, weight=3)

        self.chat_panel.add_message("J.A.R.V.I.S.: Online.")

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
        thread = Thread(target=find_optimal_threshold, args=(self.add_message_to_chat,))
        thread.start()

    def add_message_to_chat(self, message):
        # Thread-safe way to add messages to the chat panel
        self.master.after(0, self.chat_panel.add_message, message)