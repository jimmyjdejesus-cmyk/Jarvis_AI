# ui/components/chat_panel.py
import tkinter as tk
from tkinter import scrolledtext, Entry, Button

class ChatPanel(tk.Frame):
    def __init__(self, master, send_callback):
        super().__init__(master)
        self.send_callback = send_callback

        self.chat_log = scrolledtext.ScrolledText(self, state='disabled', height=25, wrap=tk.WORD)
        self.chat_log.pack(fill="both", expand=True, pady=5, padx=5)

        self.entry_box = Entry(self)
        self.entry_box.pack(fill="x", pady=5, padx=5)
        self.entry_box.bind("<Return>", self._on_send_pressed)

        self.send_button = Button(self, text="Send", command=self._on_send_pressed)
        self.send_button.pack(pady=5)

    def _on_send_pressed(self, event=None):
        user_input = self.entry_box.get()
        if user_input:
            self.entry_box.delete(0, tk.END)
            self.send_callback(user_input)

    def add_message(self, message):
        """Public method to add a message to the chat log."""
        self.chat_log.config(state='normal')
        self.chat_log.insert(tk.END, message + "\n\n")
        self.chat_log.config(state='disabled')
        self.chat_log.yview(tk.END)

    def toggle_input(self, enabled=True):
        """Enables or disables the text entry and send button."""
        state = tk.NORMAL if enabled else tk.DISABLED
        self.entry_box.config(state=state)
        self.send_button.config(state=state)