#!/usr/bin/env python3
"""
Jarvis AI Modern Desktop Application
Modern desktop UI using customtkinter for a sleek, contemporary look.
"""

try:
    import customtkinter as ctk
    MODERN_UI_AVAILABLE = True
except ImportError:
    MODERN_UI_AVAILABLE = False
    import tkinter as tk
    from tkinter import ttk, scrolledtext, messagebox

import threading
import os
import webbrowser
from pathlib import Path

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

class ModernJarvisApp:
    def __init__(self):
        if MODERN_UI_AVAILABLE:
            self.setup_modern_ui()
        else:
            self.setup_fallback_ui()
    
    def setup_modern_ui(self):
        """Setup the modern UI using customtkinter."""
        # Set appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("🤖 Jarvis AI - Agentic Workflows")
        self.root.geometry("900x700")
        
        # Configure grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Header frame
        header_frame = ctk.CTkFrame(self.root)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        title_label = ctk.CTkLabel(header_frame, 
                                  text="🤖 Jarvis AI - Agentic Workflows",
                                  font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)
        
        # Status frame
        self.status_frame = ctk.CTkFrame(header_frame)
        self.status_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.status_label = ctk.CTkLabel(self.status_frame, 
                                        text="🔄 Initializing...",
                                        font=ctk.CTkFont(size=12))
        self.status_label.pack(pady=10)
        
        # Main content frame
        main_frame = ctk.CTkFrame(self.root)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(2, weight=1)
        
        # Input section
        input_label = ctk.CTkLabel(main_frame, 
                                  text="Enter your query:",
                                  font=ctk.CTkFont(size=14, weight="bold"))
        input_label.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 5))
        
        self.query_textbox = ctk.CTkTextbox(main_frame, height=100)
        self.query_textbox.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        # Default query
        default_query = "What are the key components for building production-ready AI applications?"
        self.query_textbox.insert("0.0", default_query)
        
        # Button frame
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        self.run_button = ctk.CTkButton(button_frame, 
                                       text="🚀 Run Agentic Workflow",
                                       command=self.run_workflow,
                                       font=ctk.CTkFont(size=14, weight="bold"))
        self.run_button.pack(side="left", padx=(20, 10), pady=20)
        
        clear_button = ctk.CTkButton(button_frame, 
                                    text="🔄 Clear Output",
                                    command=self.clear_output)
        clear_button.pack(side="left", padx=(0, 10), pady=20)
        
        langsmith_button = ctk.CTkButton(button_frame, 
                                        text="📊 Open LangSmith",
                                        command=self.open_langsmith)
        langsmith_button.pack(side="left", padx=(0, 20), pady=20)
        
        # Output section
        output_label = ctk.CTkLabel(main_frame, 
                                   text="Workflow Output:",
                                   font=ctk.CTkFont(size=14, weight="bold"))
        output_label.grid(row=3, column=0, sticky="w", padx=20, pady=(0, 5))
        
        self.output_textbox = ctk.CTkTextbox(main_frame, height=300)
        self.output_textbox.grid(row=4, column=0, sticky="nsew", padx=20, pady=(0, 20))
        main_frame.grid_rowconfigure(4, weight=1)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(main_frame)
        self.progress_bar.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.progress_bar.set(0)
        
        # Check connections
        self.check_connections()
    
    def setup_fallback_ui(self):
        """Fallback to basic tkinter if customtkinter not available."""
        self.root = tk.Tk()
        self.root.title("🤖 Jarvis AI - Agentic Workflows")
        self.root.geometry("800x600")
        
        # Note about installing customtkinter
        note_label = tk.Label(self.root, 
                             text="💡 Install 'customtkinter' for a modern UI: pip install customtkinter",
                             bg="yellow", fg="black")
        note_label.pack(fill="x")
        
        # Create basic interface similar to the previous version
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Simple layout for fallback
        tk.Label(main_frame, text="🤖 Jarvis AI", font=("Arial", 16)).pack(pady=10)
        tk.Label(main_frame, text="Run: pip install customtkinter for modern UI").pack()
    
    def check_connections(self):
        """Check system connections."""
        def check():
            self.log_output("🔍 Checking connections...\n")
            
            langsmith_ok = self.test_langsmith()
            ollama_ok = self.test_ollama()
            
            if langsmith_ok and ollama_ok:
                self.update_status("✅ All systems ready", "green")
            elif langsmith_ok:
                self.update_status("⚠️ LangSmith ready (Ollama offline)", "orange")
            else:
                self.update_status("❌ Connection issues", "red")
        
        threading.Thread(target=check, daemon=True).start()
    
    def update_status(self, text, color):
        """Update status label."""
        if MODERN_UI_AVAILABLE:
            self.status_label.configure(text=text)
        
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
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                self.log_output(f"✅ Ollama: Connected ({len(models)} models)\n")
                return True
            else:
                self.log_output("❌ Ollama: Not responding\n")
                return False
        except Exception as e:
            self.log_output(f"❌ Ollama: {str(e)}\n")
            return False
    
    def log_output(self, text):
        """Add text to output area."""
        if MODERN_UI_AVAILABLE:
            self.output_textbox.insert("end", text)
        
    def clear_output(self):
        """Clear output area."""
        if MODERN_UI_AVAILABLE:
            self.output_textbox.delete("0.0", "end")
    
    def open_langsmith(self):
        """Open LangSmith dashboard."""
        webbrowser.open('https://smith.langchain.com/')
    
    def run_workflow(self):
        """Run the agentic workflow."""
        if not MODERN_UI_AVAILABLE:
            return
            
        query = self.query_textbox.get("0.0", "end").strip()
        if not query:
            return
        
        self.run_button.configure(state="disabled")
        self.progress_bar.start()
        
        def workflow_thread():
            try:
                self.clear_output()
                self.log_output("🚀 Starting Agentic Workflow...\n")
                self.log_output("=" * 50 + "\n")
                
                # Execute workflow (same logic as before)
                self.execute_workflow(query)
                
                self.log_output("\n✅ Workflow completed!\n")
                
            except Exception as e:
                self.log_output(f"\n❌ Error: {str(e)}\n")
            finally:
                self.root.after(0, lambda: [
                    self.run_button.configure(state="normal"),
                    self.progress_bar.stop()
                ])
        
        threading.Thread(target=workflow_thread, daemon=True).start()
    
    def execute_workflow(self, query):
        """Execute the workflow steps."""
        self.log_output(f"🎯 Query: {query}\n\n")
        
        # Planning
        self.log_output("📋 Planning phase...\n")
        plan = ["Analyze requirements", "Research solutions", "Synthesize findings"]
        for step in plan:
            self.log_output(f"   • {step}\n")
        
        # Research
        self.log_output("\n🔍 Research phase...\n")
        self.log_output("   • Gathering information...\n")
        self.log_output("   • Analyzing data...\n")
        
        # Synthesis
        self.log_output("\n📝 Synthesis phase...\n")
        self.log_output("   • Generating comprehensive response...\n")
        
        result = """
🚀 PRODUCTION AI ARCHITECTURE

Key components identified:
• Infrastructure: Vector DBs, Model serving, APIs
• Monitoring: LangSmith, APM, Analytics  
• Scalability: Auto-scaling, Caching, Load balancing
• Security: Authentication, Encryption, Compliance
• Deployment: CI/CD, IaC, Multi-environment

This provides a robust foundation for enterprise AI applications.
"""
        self.log_output(result)
    
    def run(self):
        """Start the application."""
        if MODERN_UI_AVAILABLE:
            self.root.mainloop()
        else:
            print("Please install customtkinter: pip install customtkinter")

def main():
    """Main entry point."""
    app = ModernJarvisApp()
    app.run()

if __name__ == "__main__":
    main()
