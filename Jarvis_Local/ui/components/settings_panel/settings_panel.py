# ui/components/settings_panel.py
import tkinter as tk
from tkinter import ttk
import settings

class SettingsPanel(ttk.Frame):
    def __init__(self, master, autotune_callback):
        super().__init__(master, padding=10)
        self.autotune_callback = autotune_callback

        ttk.Label(self, text="Agent Controls", font=("Helvetica", 12, "bold")).pack(pady=10)

        # ... (All the widget creation logic from your old UI file goes here) ...
        # For example:
        ttk.Label(self, text="Voting Runs:").pack(anchor="w", padx=5)
        self.voting_runs_var = tk.IntVar(value=settings.NUM_RESPONSES)
        voting_spinbox = ttk.Spinbox(self, from_=1, to=10, textvariable=self.voting_runs_var, command=self._update_settings)
        voting_spinbox.pack(fill="x", padx=5, pady=2)

        self.autotune_button = ttk.Button(self, text="Auto-Tune Confidence", command=self.autotune_callback)
        self.autotune_button.pack(pady=20)
        # ... (Add all other settings widgets: DeepConf toggle, threshold, model choice) ...

    def _update_settings(self, *args):
        settings.NUM_RESPONSES = self.voting_runs_var.get()
        # ... (Update all other settings) ...