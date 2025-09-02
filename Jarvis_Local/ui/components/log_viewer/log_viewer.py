# ui/components/log_viewer.py
import tkinter as tk
from tkinter import scrolledtext
import os

class LogViewerWindow(tk.Toplevel):
    def __init__(self, master, log_file="jarvis_local.log"):
        super().__init__(master)
        self.title("J.A.R.V.I.S. Developer Log")
        self.geometry("800x600")
        self.log_file = log_file
        self.last_position = 0

        self.log_text = scrolledtext.ScrolledText(self, state='disabled', wrap=tk.WORD, bg="black", fg="lightgreen")
        self.log_text.pack(fill="both", expand=True)

        self.load_initial_content()
        self.periodic_update()

    def load_initial_content(self):
        """Loads the full log file content when the window is first opened."""
        try:
            with open(self.log_file, 'r') as f:
                content = f.read()
                self.last_position = f.tell()
                self._append_text(content)
        except FileNotFoundError:
            self._append_text(f"Log file not found at: {self.log_file}")

    def periodic_update(self):
        """Checks for new content in the log file and appends it."""
        try:
            current_size = os.path.getsize(self.log_file)
            if current_size > self.last_position:
                with open(self.log_file, 'r') as f:
                    f.seek(self.last_position)
                    new_content = f.read()
                    self.last_position = f.tell()
                    self._append_text(new_content)
        except (FileNotFoundError, IOError):
            # Handle cases where the file might be temporarily inaccessible
            pass

        # Schedule this method to run again after 2 seconds (2000 ms)
        self.after(2000, self.periodic_update)

    def _append_text(self, text):
        """Appends text to the widget and scrolls to the end."""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, text)
        self.log_text.config(state='disabled')
        self.log_text.yview(tk.END)