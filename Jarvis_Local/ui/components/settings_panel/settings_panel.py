# ui/components/settings_panel.py
import tkinter as tk
from tkinter import ttk
import settings
from logger_config import log

class SettingsPanel(ttk.Frame):
    def __init__(self, master, autotune_callback, log_viewer_callback, save_model_callback, run_evaluation_callback, save_api_key_callback, run_demo_callback):
        super().__init__(master, padding=10)
        
        # Store callbacks from the main window
        self.autotune_callback = autotune_callback
        self.log_viewer_callback = log_viewer_callback
        self.save_model_callback = save_model_callback
        self.run_evaluation_callback = run_evaluation_callback
        self.save_api_key_callback = save_api_key_callback
        self.run_demo_callback = run_demo_callback

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
        ttk.Button(self, text="Run Evaluation", command=self.run_evaluation_callback).pack(fill="x", padx=5, pady=5)

        self.run_demo_button = ttk.Button(self, text="Run Demo", command=self.run_demo_callback)
        self.run_demo_button.pack(fill="x", padx=5, pady=5)

        # --- Model Optimization Settings ---
        ttk.Label(self, text="Model Optimization", font=("Helvetica", 12, "bold")).pack(pady=(20,5), anchor="w")

        ttk.Label(self, text="OpenAI API Key").pack(anchor="w", padx=5)
        self.api_key_var = tk.StringVar()

        # The show = "*" masks the input for security
        api_key_entry = ttk.Entry(self, textvariable=self.api_key_var, show="*")
        api_key_entry.pack(fill="x", padx=5, pady=2)

        save_key_button = ttk.Button(self, text="Save API Key", command=self._on_save_key)
        save_key_button.pack(pady=5)

        # --- API Key management Section ---
        ttk.Label(self, text="API Key Management", font=("Helvetica", 12, "bold")).pack(pady=(20,5), anchor="w")
        ttk.Label(self, text="OpenAI API Key: ").pack(anchor="w", padx=5)
        self.api_key_var = tk.StringVar()

        # The show = "*" masks the input for security
        api_key_entry = ttk.Entry(self, textvariable=self.api_key_var, show="*")
        api_key_entry.pack(fill="x", padx=5, pady=2)

        save_key_button = ttk.Button(self, text="Save API Key", command=self._on_save_key)
        save_key_button.pack(pady=5)

        # N_GPU_LAYERS
        ttk.Label(self, text="GPU Layers:").pack(anchor="w", padx=5)
        self.gpu_layers_var = tk.IntVar(value=settings.N_GPU_LAYERS)
        ttk.Spinbox(self, from_=-1, to=100, textvariable=self.gpu_layers_var, command=self._update_settings).pack(fill="x", padx=5, pady=2)
        
        # N_THREADS
        ttk.Label(self, text="Threads:").pack(anchor="w", padx=5)
        self.threads_var = tk.IntVar(value=settings.N_THREADS)
        ttk.Spinbox(self, from_=1, to=16, textvariable=self.threads_var, command=self._update_settings).pack(fill="x", padx=5, pady=2)
        
        # N_CTX
        ttk.Label(self, text="Context Size:").pack(anchor="w", padx=5)
        self.ctx_var = tk.IntVar(value=settings.N_CTX)
        ttk.Spinbox(self, from_=512, to=8192, textvariable=self.ctx_var, command=self._update_settings).pack(fill="x", padx=5, pady=2)
        
        # VERBOSE
        self.verbose_var = tk.BooleanVar(value=settings.VERBOSE)
        ttk.Checkbutton(self, text="Verbose Logging", variable=self.verbose_var, command=self._update_settings).pack(anchor="w", padx=5, pady=10)

    def _update_settings(self, *args):
        """Called whenever a UI control is changed to update the live settings."""
        settings.NUM_RESPONSES = self.voting_runs_var.get()
        settings.DEEPCONF_ENABLED = self.deepconf_enabled_var.get()
        settings.CONFIDENCE_THRESHOLD = self.confidence_var.get()
        settings.N_GPU_LAYERS = self.gpu_layers_var.get()
        settings.N_THREADS = self.threads_var.get()
        settings.N_CTX = self.ctx_var.get()
        settings.VERBOSE = self.verbose_var.get()
        self.confidence_label.config(text=f"{settings.CONFIDENCE_THRESHOLD:.2f}")
        log.info(f"Settings updated via UI.")

    def _on_save_model(self):
        """Calls the main window's save function with the selected model name."""
        self.save_model_callback(self.model_var.get())

    def _on_save_key(self):
        """Gets the key from the entry and calls the main window's save function."""
        api_key = self.api_key_var.get()
        if api_key:
            # We will create the 'save_api_key' method on the main window
            self.save_api_key_callback(api_key)
            self.api_key_var.set("")  # Clear the entry after saving
