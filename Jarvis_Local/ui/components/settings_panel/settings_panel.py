# ui/components/settings_panel.py
import tkinter as tk
from tkinter import ttk
import settings
from logger_config import log

class SettingsPanel(ttk.Frame):
    def __init__(self, master, autotune_callback, log_viewer_callback, save_model_callback):
        super().__init__(master, padding=10)
        
        # Store callbacks from the main window
        self.autotune_callback = autotune_callback
        self.log_viewer_callback = log_viewer_callback
        self.save_model_callback = save_model_callback

        ttk.Label(self, text="Agent Controls", font=("Helvetica", 12, "bold")).pack(pady=5, anchor="w")

        # --- Voting Runs ---
        ttk.Label(self, text="Voting Runs:").pack(anchor="w", padx=5)
        self.voting_runs_var = tk.IntVar(value=settings.NUM_RESPONSES)
        ttk.Spinbox(self, from_=1, to=10, textvariable=self.voting_runs_var, command=self._update_settings).pack(fill="x", padx=5, pady=2)

        # --- DeepConf Toggle ---
        self.deepconf_enabled_var = tk.BooleanVar(value=settings.DEEPCONF_ENABLED)
        ttk.Checkbutton(self, text="Enable DeepConf Early Stopping", variable=self.deepconf_enabled_var, command=self._update_settings).pack(anchor="w", padx=5, pady=10)

        # --- Confidence Threshold ---
        ttk.Label(self, text="Confidence Threshold:").pack(anchor="w", padx=5)
        self.confidence_var = tk.DoubleVar(value=settings.CONFIDENCE_THRESHOLD)
        self.confidence_label = ttk.Label(self, text=f"{self.confidence_var.get():.2f}")
        self.confidence_label.pack()
        ttk.Scale(self, from_=0, to=20, orient=tk.HORIZONTAL, variable=self.confidence_var, command=self._update_settings).pack(fill="x", padx=5, pady=2)

        # --- Model Selection (Requires Restart) ---
        ttk.Label(self, text="Active Model (Requires Restart):").pack(anchor="w", padx=5, pady=(20, 0))
        self.model_var = tk.StringVar(value=settings.ACTIVE_MODEL_NAME)
        ttk.OptionMenu(self, self.model_var, self.model_var.get(), *settings.AVAILABLE_MODELS.keys()).pack(fill="x", padx=5, pady=2)
        ttk.Button(self, text="Save Model Choice", command=self._on_save_model).pack(pady=5)

        # --- Developer Tools ---
        ttk.Label(self, text="Developer Tools", font=("Helvetica", 12, "bold")).pack(pady=(20,5), anchor="w")
        ttk.Button(self, text="Auto-Tune Confidence", command=self.autotune_callback).pack(fill="x", padx=5, pady=5)
        ttk.Button(self, text="View Dev Log", command=self.log_viewer_callback).pack(fill="x", padx=5, pady=5)

    def _update_settings(self, *args):
        """Called whenever a UI control is changed to update the live settings."""
        settings.NUM_RESPONSES = self.voting_runs_var.get()
        settings.DEEPCONF_ENABLED = self.deepconf_enabled_var.get()
        settings.CONFIDENCE_THRESHOLD = self.confidence_var.get()
        self.confidence_label.config(text=f"{settings.CONFIDENCE_THRESHOLD:.2f}")
        log.info(f"Settings updated via UI.")

    def _on_save_model(self):
        """Calls the main window's save function with the selected model name."""
        self.save_model_callback(self.model_var.get())