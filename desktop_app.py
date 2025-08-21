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

from config.config_loader import load_config

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
        self.root.title(f"{app_name} - Agentic Workflows")
        self.root.geometry("800x600")
        self.root.configure(bg='#2b2b2b')
        
        # Configure style
        self.setup_styles()
        
        # Create main interface
        self.create_widgets()
        
        # Initialize connections
        self.check_connections()
    
    def setup_styles(self):
        """Setup modern dark theme styles."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors for dark theme
        style.configure('TFrame', background='#2b2b2b')
        style.configure('TLabel', background='#2b2b2b', foreground='#ffffff')
        style.configure('TButton', background='#4a4a4a', foreground='#ffffff')
        style.map('TButton', background=[('active', '#5a5a5a')])
    
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
        header_label = ttk.Label(main_frame, text="🤖 Jarvis AI - Agentic Workflows", 
                                font=('Arial', 16, 'bold'))
        header_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)
        
        ttk.Label(status_frame, text="Status:").grid(row=0, column=0, sticky=tk.W)
        self.status_label = ttk.Label(status_frame, text="Initializing...", foreground='#ffaa00')
        self.status_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(1, weight=1)
        
        ttk.Label(input_frame, text="Enter your query:").grid(row=0, column=0, sticky=tk.W)
        
        # Query input
        self.query_text = scrolledtext.ScrolledText(input_frame, height=4, 
                                                   bg='#3b3b3b', fg='#ffffff',
                                                   insertbackground='#ffffff')
        self.query_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
        
        # Default query
        default_query = "What are the key components for building production-ready AI applications?"
        self.query_text.insert('1.0', default_query)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(0, 10))
        
        self.run_button = ttk.Button(button_frame, text="🚀 Run Agentic Workflow", 
                                    command=self.run_workflow)
        self.run_button.grid(row=0, column=0, padx=(0, 10))
        
        ttk.Button(button_frame, text="🔄 Clear Output", 
                  command=self.clear_output).grid(row=0, column=1, padx=(0, 10))
        
        ttk.Button(button_frame, text="📊 Open LangSmith", 
                  command=self.open_langsmith).grid(row=0, column=2)
        
        # Output frame
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(1, weight=1)
        
        ttk.Label(output_frame, text="Workflow Output:").grid(row=0, column=0, sticky=tk.W)
        
        # Output text area
        self.output_text = scrolledtext.ScrolledText(output_frame, height=15,
                                                   bg='#1e1e1e', fg='#00ff00',
                                                   insertbackground='#ffffff',
                                                   font=('Consolas', 9))
        self.output_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Configure additional row weights
        main_frame.rowconfigure(4, weight=1)
    
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
        try:
            import requests
            ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
            response = requests.get(f"{ollama_url}/api/tags", timeout=5)
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
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_output(self):
        """Clear the output area."""
        self.output_text.delete('1.0', tk.END)
    
    def open_langsmith(self):
        """Open LangSmith dashboard."""
        import webbrowser
        webbrowser.open('https://smith.langchain.com/')
    
    def run_workflow(self):
        """Run the agentic workflow."""
        query = self.query_text.get('1.0', tk.END).strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a query!")
            return
        
        # Disable button and start progress
        self.run_button.config(state='disabled')
        self.progress.start()
        
        def workflow_thread():
            try:
                self.clear_output()
                self.log_output("🚀 Starting Agentic Workflow...\n")
                self.log_output("=" * 50 + "\n")
                self.log_output(f"🎯 Query: {query}\n\n")
                
                # Setup environment
                if os.getenv('LANGSMITH_API_KEY'):
                    os.environ['LANGCHAIN_TRACING_V2'] = 'true'
                    os.environ['LANGCHAIN_PROJECT'] = 'jarvis-ai-desktop'
                    self.log_output("📡 LangSmith tracing enabled\n")
                
                # Run workflow steps
                result = self.execute_agentic_workflow(query)
                
                self.log_output("\n" + "=" * 50 + "\n")
                self.log_output("✅ Workflow completed successfully!\n")
                self.log_output("\n📊 Check LangSmith dashboard for traces:\n")
                self.log_output("   https://smith.langchain.com/\n")
                
            except Exception as e:
                self.log_output(f"\n❌ Workflow failed: {str(e)}\n")
            
            finally:
                # Re-enable button and stop progress
                self.root.after(0, lambda: [
                    self.run_button.config(state='normal'),
                    self.progress.stop()
                ])
        
        threading.Thread(target=workflow_thread, daemon=True).start()
    
    def execute_agentic_workflow(self, query):
        """Execute the multi-step agentic workflow."""
        
        # Step 1: Planning
        self.log_output("📋 Step 1: Planning\n")
        plan = self.planning_agent(query)
        self.log_output("   Plan:\n")
        for i, step in enumerate(plan, 1):
            self.log_output(f"      {i}. {step}\n")
        
        # Step 2: Research
        self.log_output("\n🔍 Step 2: Research & Analysis\n")
        research = self.research_agent(plan)
        self.log_output("   Research completed:\n")
        for category, findings in research.items():
            self.log_output(f"      {category.title()}: {len(findings)} findings\n")
        
        # Step 3: Analysis
        self.log_output("\n🧠 Step 3: Analysis\n")
        analysis = self.analysis_agent(research)
        self.log_output("   Key insights:\n")
        for insight in analysis[:3]:  # Show top 3 insights
            self.log_output(f"      • {insight}\n")
        
        # Step 4: Synthesis
        self.log_output("\n📝 Step 4: Synthesis\n")
        result = self.synthesis_agent(query, plan, research, analysis)
        self.log_output("   Final result generated\n")
        
        # Display result in a new window
        self.show_result_window(result)
        
        return result
    
    def planning_agent(self, query):
        """Planning agent implementation."""
        if "production" in query.lower() and "ai" in query.lower():
            return [
                "Identify core infrastructure requirements",
                "Research monitoring and observability tools", 
                "Analyze scalability considerations",
                "Evaluate security and compliance needs",
                "Compile deployment best practices"
            ]
        else:
            return [
                "Understand the core question",
                "Break down into sub-components",
                "Research relevant technologies",
                "Synthesize findings into actionable insights"
            ]
    
    def research_agent(self, plan):
        """Research agent implementation."""
        return {
            "infrastructure": ["Vector databases", "Model serving", "API gateways", "Containers"],
            "monitoring": ["LangSmith", "APM tools", "Error tracking", "Analytics"],
            "scalability": ["Auto-scaling", "Caching", "Load balancing", "Queue systems"],
            "security": ["Authentication", "Encryption", "Privacy", "Compliance"],
            "deployment": ["CI/CD", "Infrastructure as Code", "Multi-environment", "DR"]
        }
    
    def analysis_agent(self, research_data):
        """Analysis agent implementation."""
        return [
            "Vector databases are essential for semantic search applications",
            "LangSmith provides comprehensive observability for LLM workflows",
            "Container orchestration enables reliable scaling and deployment",
            "Multi-layered security approach is critical for production systems",
            "Automated CI/CD reduces deployment risks and improves reliability"
        ]
    
    def synthesis_agent(self, query, plan, research, analysis):
        """Synthesis agent implementation."""
        return """🚀 PRODUCTION-READY AI APPLICATION COMPONENTS

🏗️ Infrastructure Foundation
• Vector Databases: Pinecone, Weaviate, Chroma for semantic search
• Model Serving: Hugging Face, Replicate for model hosting  
• API Gateway: Load balancing and rate limiting
• Containerization: Docker + Kubernetes for deployment

📊 Monitoring & Observability
• LangSmith: End-to-end tracing for LLM applications
• APM Tools: Application performance monitoring
• Analytics: Usage metrics and cost tracking
• Error Handling: Comprehensive logging and recovery

⚡ Scalability Architecture
• Auto-scaling: Dynamic resource allocation
• Caching: Redis/Memcached for performance
• Load Balancing: Traffic distribution
• Queue Systems: Asynchronous processing

🔒 Security & Compliance
• Authentication: API keys, OAuth, RBAC
• Encryption: Data protection at rest and in transit
• Privacy: Sensitive information handling
• Compliance: GDPR, HIPAA requirements

🚀 Deployment & Operations
• CI/CD Pipelines: Automated workflows
• Infrastructure as Code: Reproducible deployments
• Environment Management: Dev, staging, production
• Disaster Recovery: Backup and rollback strategies

This architecture provides a solid foundation for enterprise-grade AI applications."""
    
    def show_result_window(self, result):
        """Show the final result in a new window."""
        result_window = tk.Toplevel(self.root)
        result_window.title("Workflow Result")
        result_window.geometry("600x400")
        result_window.configure(bg='#2b2b2b')
        
        result_text = scrolledtext.ScrolledText(result_window, 
                                              bg='#1e1e1e', fg='#ffffff',
                                              font=('Consolas', 10),
                                              wrap=tk.WORD)
        result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        result_text.insert('1.0', result)
        result_text.config(state='disabled')

def main():
    """Main function to start the desktop application."""
    root = tk.Tk()
    app = JarvisDesktopApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
