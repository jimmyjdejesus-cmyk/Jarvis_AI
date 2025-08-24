#!/usr/bin/env python3
"""
Jarvis AI Desktop Application
Simple desktop UI for agentic workflows with LangSmith monitoring.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import os
from pathlib import Path
import asyncio
import uuid
import time

from config.config_loader import load_config
from jarvis.orchestration.agents import MetaAgent

# Load environment variables
def load_env():
    env_file = Path('.env')
    if env_file.exists():
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

load_env()

# Load configuration profile and apply environment overrides
CONFIG = load_config()
os.environ.setdefault(
    "OLLAMA_BASE_URL",
    CONFIG.get("integrations", {}).get("ollama", {}).get("base_url", "http://localhost:11434"),
)

class JarvisDesktopApp:
    def __init__(self, root):
        self.root = root
        app_name = CONFIG.get("app_name", "Jarvis AI")
        self.root.title(f"{app_name} - Multi-Agent Orchestrator")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')
        
        # Initialize the Meta-Agent
        self.meta_agent = MetaAgent()
        self.models = []
        
        # Create main interface
        self.create_widgets()
        
        # Configure style
        self.setup_styles()
        
        # Initialize connections
        self.check_connections()

        # Prompt for API key if missing
        self.prompt_for_api_key()
    
    def setup_styles(self):
        """Setup modern dark theme styles."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors for dark theme
        style.configure('TFrame', background='#2b2b2b')
        style.configure('TLabel', background='#2b2b2b', foreground='#ffffff')
        style.configure('TButton', background='#4a4a4a', foreground='#ffffff')
        style.map('TButton', background=[('active', '#5a5a5a')])

        # Chat history text styles
        self.chat_history.tag_configure("user", foreground="#a9d1ff", font=('Arial', 10, 'bold'))
        self.chat_history.tag_configure("agent", foreground="#ffffff", font=('Arial', 10, 'bold'))
        self.chat_history.tag_configure("agent_stream", foreground="#ffffff")
        self.chat_history.tag_configure("warning", foreground="#ffaa00")
        self.chat_history.tag_configure("error", foreground="#ff4444", font=('Arial', 10, 'italic'))
    
    def create_widgets(self):
        """Create the main UI components."""
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Header
        header_label = ttk.Label(main_frame, text="🤖 Jarvis AI - Multi-Agent Orchestrator", 
                                font=('Arial', 16, 'bold'))
        header_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))

        # Main layout panes
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.rowconfigure(1, weight=1)

        # Left pane for controls and chat
        left_pane = ttk.Frame(paned_window, padding=5)
        paned_window.add(left_pane, weight=1)
        left_pane.columnconfigure(0, weight=1)
        left_pane.rowconfigure(2, weight=1)

        # Right pane for workflow visualization
        right_pane = ttk.Frame(paned_window, padding=5)
        paned_window.add(right_pane, weight=2)
        right_pane.columnconfigure(0, weight=1)
        right_pane.rowconfigure(1, weight=1)

        # --- Left Pane Widgets ---
        controls_frame = ttk.Frame(left_pane)
        controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        controls_frame.columnconfigure(1, weight=1)

        ttk.Label(controls_frame, text="Mode:").grid(row=0, column=0, sticky=tk.W)
        self.mode_selector = ttk.Combobox(controls_frame, values=["Chat", "Deep Research", "Agent Mode"], state="readonly")
        self.mode_selector.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        self.mode_selector.set("Agent Mode")

        ttk.Label(controls_frame, text="Status:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.status_label = ttk.Label(controls_frame, text="Initializing...", foreground='#ffaa00')
        self.status_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))

        # Chat history
        self.chat_history = scrolledtext.ScrolledText(left_pane, bg='#1e1e1e', fg='#ffffff', font=('Arial', 10), wrap=tk.WORD, state='disabled')
        self.chat_history.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Input frame
        input_frame = ttk.Frame(left_pane, padding=(0, 10))
        input_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        input_frame.columnconfigure(0, weight=1)

        self.query_text = tk.Text(input_frame, height=3, bg='#3b3b3b', fg='#ffffff', insertbackground='#ffffff', font=('Arial', 10))
        self.query_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.query_text.bind("<Return>", self.run_workflow_on_enter)

        self.run_button = ttk.Button(input_frame, text="Execute", command=self.run_workflow)
        self.run_button.grid(row=0, column=1, padx=(10, 0))

        # --- Right Pane Widgets ---
        ttk.Label(right_pane, text="Workflow Visualizer", font=('Arial', 12, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        self.workflow_canvas = tk.Canvas(right_pane, bg="#1e1e1e", highlightthickness=0)
        self.workflow_canvas.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(right_pane, text="Memory Bus Inspector", font=('Arial', 12, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        
        self.memory_bus_viewer = scrolledtext.ScrolledText(right_pane, height=10, bg='#1e1e1e', fg='#a9d1ff', font=('Consolas', 9), wrap=tk.WORD, state='disabled')
        self.memory_bus_viewer.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_pane.rowconfigure(3, weight=1)
    
    def check_connections(self):
        """Check LangSmith and Ollama connections."""
        def check():
            self.log_output("🔍 Checking connections...\n")
            
            # Test LangSmith
            langsmith_ok = self.test_langsmith()
            
            # Test Ollama
            ollama_ok = self.test_ollama()
            
            if langsmith_ok and ollama_ok:
                self.status_label.config(text="✅ All systems ready", foreground='#00ff00')
            elif langsmith_ok:
                self.status_label.config(text="⚠️ LangSmith only", foreground='#ffaa00')
            elif ollama_ok:
                self.status_label.config(text="⚠️ Ollama only", foreground='#ffaa00')
            else:
                self.status_label.config(text="❌ Connection issues", foreground='#ff4444')
        
        threading.Thread(target=check, daemon=True).start()
    
    def test_langsmith(self):
        """Test LangSmith connection."""
        try:
            from langsmith import Client
            client = Client()
            projects = list(client.list_projects(limit=1))
            self.log_output(f"✅ LangSmith: Connected ({len(projects)} projects)\n")
            return True
        except Exception as e:
            self.log_output(f"❌ LangSmith: {str(e)}\n")
            return False
    
    def test_ollama(self):
        """Test Ollama connection."""
        # This will be re-integrated when the agents use LLMs.
        return True
    
    def log_output(self, text, tag=None):
        """Add text to the chat history with an optional tag for styling."""
        self.chat_history.config(state='normal')
        self.chat_history.insert(tk.END, text, tag)
        self.chat_history.config(state='disabled')
        self.chat_history.see(tk.END)
        self.root.update_idletasks()

    def prompt_for_api_key(self):
        """Check for LangSmith API key and prompt if missing."""
        if not os.getenv('LANGSMITH_API_KEY'):
            self.open_settings_window(prompt_message="LangSmith API Key is not set. Please enter it to enable tracing.")

    def open_settings_window(self, prompt_message=None):
        """Open a window to configure settings like API keys."""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x200")
        settings_window.configure(bg='#2b2b2b')
        settings_window.transient(self.root)
        settings_window.grab_set()

        frame = ttk.Frame(settings_window, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        if prompt_message:
            ttk.Label(frame, text=prompt_message, foreground="#ffaa00", wraplength=380).pack(pady=(0, 10))

        ttk.Label(frame, text="LangSmith API Key:").pack(pady=(10, 5))
        
        api_key_entry = ttk.Entry(frame, width=50)
        api_key_entry.pack()
        current_key = os.getenv('LANGSMITH_API_KEY', '')
        api_key_entry.insert(0, current_key)

        def save_key():
            new_key = api_key_entry.get().strip()
            if not new_key:
                messagebox.showwarning("Warning", "API Key cannot be empty.", parent=settings_window)
                return

            # Temporarily set the key to test it
            original_key = os.getenv('LANGSMITH_API_KEY')
            os.environ['LANGSMITH_API_KEY'] = new_key
            
            try:
                from langsmith import Client
                client = Client()
                client.list_projects(limit=1) # Test call
                
                # If test is successful, save for real
                env_file = Path('.env')
                lines = []
                key_found = False
                if env_file.exists():
                    with open(env_file, 'r') as f:
                        lines = f.readlines()
                
                with open(env_file, 'w') as f:
                    for line in lines:
                        if line.strip().startswith('LANGSMITH_API_KEY='):
                            f.write(f'LANGSMITH_API_KEY={new_key}\n')
                            key_found = True
                        else:
                            f.write(line)
                    if not key_found:
                        f.write(f'LANGSMITH_API_KEY={new_key}\n')
                
                self.log_output("✅ LangSmith API Key is valid and saved.\n")
                settings_window.destroy()
                self.check_connections() # Re-check connections

            except Exception:
                # If test fails, show error and revert env var
                if original_key:
                    os.environ['LANGSMITH_API_KEY'] = original_key
                else:
                    del os.environ['LANGSMITH_API_KEY']
                messagebox.showerror("Error", "Invalid LangSmith API Key. Authentication failed. Please check the key and try again.", parent=settings_window)

        save_button = ttk.Button(frame, text="Save", command=save_key)
        save_button.pack(pady=(10, 0))

    def update_model_selector(self):
        """Update the model selector combobox with available models."""
        # Placeholder until LLM integration is re-added
        self.mode_selector.set("Agent Mode")
    
    def clear_output(self):
        """Clear the chat history."""
        self.chat_history.config(state='normal')
        self.chat_history.delete('1.0', tk.END)
        self.chat_history.config(state='disabled')
    
    def open_langsmith(self):
        """Open LangSmith dashboard."""
        import webbrowser
        webbrowser.open('https://smith.langchain.com/')
    
    def run_workflow_on_enter(self, event):
        """Handle the Enter key press to run the workflow."""
        self.run_workflow()
        return "break"  # Prevents the default newline character

    def run_workflow(self, event=None):
        """Run the agentic workflow based on the selected mode."""
        objective = self.query_text.get('1.0', tk.END).strip()
        mode = self.mode_selector.get()

        if not objective:
            return

        self.log_output(f"You: {objective}\n\n", "user")
        self.query_text.delete('1.0', tk.END)
        self.run_button.config(state='disabled')

        if mode == "Agent Mode":
            # For Agent Mode, we create a dedicated directory for the project
            project_dir = f"project_{objective.replace(' ', '_').lower()[:20]}_{uuid.uuid4().hex[:6]}"
            os.makedirs(project_dir, exist_ok=True)
            
            threading.Thread(target=self.run_agent_mode, args=(objective, project_dir), daemon=True).start()
        else:
            # Placeholder for other modes
            self.log_output(f"Mode '{mode}' is not yet implemented.\n\n", "error")
            self.run_button.config(state='normal')
    
    def run_agent_mode(self, objective: str, project_dir: str):
        """Handles the execution of the full multi-agent orchestration."""
        try:
            self.log_output(f"Jarvis (Meta-Agent): Spawning orchestrator for objective...\n\n", "agent")
            orchestrator = self.meta_agent.spawn_orchestrator(objective, project_dir)
            
            # Periodically update the memory bus viewer
            stop_event = threading.Event()
            monitor_thread = threading.Thread(target=self.monitor_memory_bus, args=(orchestrator.memory_bus, stop_event), daemon=True)
            monitor_thread.start()

            # Run the orchestrator
            final_result = orchestrator.run()

            # Stop the monitor and show final state
            stop_event.set()
            self.update_memory_bus_viewer(orchestrator.memory_bus.read_log()) # Final update
            
            self.log_output(f"Jarvis (Meta-Agent): Orchestration complete.\nFinal Result: {final_result}\n\n", "agent")

        except Exception as e:
            self.log_output(f"\n\nAn error occurred during orchestration: {str(e)}\n\n", "error")
        
        finally:
            self.root.after(0, lambda: self.run_button.config(state='normal'))

    def monitor_memory_bus(self, memory_bus, stop_event):
        """Periodically reads the memory bus and updates the UI."""
        while not stop_event.is_set():
            log_content = memory_bus.read_log()
            self.root.after(0, self.update_memory_bus_viewer, log_content)
            time.sleep(0.5)

    def update_memory_bus_viewer(self, content: str):
        """Updates the content of the memory bus inspector."""
        self.memory_bus_viewer.config(state='normal')
        self.memory_bus_viewer.delete('1.0', tk.END)
        self.memory_bus_viewer.insert('1.0', content)
        self.memory_bus_viewer.config(state='disabled')
        self.memory_bus_viewer.see(tk.END)

def main():
    """Main function to start the desktop application."""
    root = tk.Tk()
    app = JarvisDesktopApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
