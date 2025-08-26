def manage_config(args):
    """Manage configuration."""
    try:
        from config.config_loader import load_config, get_config_path, save_config
        if args.init:
            print("🔧 Initializing default configuration...")
            config_path = get_config_path()
            if not config_path.exists():
                default_config_path = current_dir / "config" / "default.yaml"
                import shutil
                shutil.copy2(default_config_path, config_path)
                print(f"✅ Default configuration created at {config_path}")
            else:
                print("✅ Configuration file already exists.")
            return
        config = load_config()
        if args.show:
            import yaml
            print("📋 Current Jarvis AI Configuration:")
            print(yaml.dump(config))
        elif args.validate:
            print("✅ Configuration loaded successfully.")
    except Exception as e:
        print(f"❌ Error managing configuration: {e}")
        sys.exit(1)
"""
CLI entry point for Jarvis AI
Provides command-line interface for running and managing Jarvis AI
"""

import sys
import argparse
import os
from pathlib import Path

# Add legacy directory to path for imports
current_dir = Path(__file__).parent.parent
legacy_dir = current_dir / "legacy"
sys.path.insert(0, str(legacy_dir))
sys.path.insert(0, str(current_dir))

def main():
    """Main CLI entry point for Jarvis AI."""
    parser = argparse.ArgumentParser(
        description="Jarvis AI - Privacy-first modular AI development assistant",
        prog="jarvis"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Run command to start the application or execute a mission
    run_parser = subparsers.add_parser("run", help="Start the Jarvis AI application or execute a mission")
    run_parser.add_argument("directive", nargs="?", default=None, help="The mission directive to execute (optional)")
    run_parser.add_argument("--code", help="Path to a code file to include in the context")
    run_parser.add_argument("--context", help="Additional context for the mission")
    run_parser.add_argument("--port", type=int, default=8501, help="Port to run on (if not executing a directive)")
    run_parser.add_argument("--host", default="localhost", help="Host to bind to (if not executing a directive)")
    run_parser.add_argument("--headless", action="store_true", help="Run in headless mode (if not executing a directive)")
    
    # Config command to manage configuration
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_parser.add_argument("--show", action="store_true", help="Show current configuration")
    config_parser.add_argument("--validate", action="store_true", help="Validate configuration")
    config_parser.add_argument("--init", action="store_true", help="Initialize default configuration")
    
    # Version command
    version_parser = subparsers.add_parser("version", help="Show version information")

    # Index command to rebuild repository search index
    index_parser = subparsers.add_parser("index", help="Rebuild repository search index")
    index_parser.add_argument("--force", action="store_true", help="Force rebuild even if index exists")
    
    args = parser.parse_args()
    
    if args.command == "run":
        run_application(args)
    elif args.command == "config":
        manage_config(args)
    elif args.command == "version":
        show_version()
    elif args.command == "index":
        run_indexer(args)
    else:
        parser.print_help()

def run_application(args):
    """Run the Jarvis AI desktop application or execute a mission."""
    if args.directive:
        import asyncio
        from jarvis.ecosystem.meta_intelligence import ExecutiveAgent

        print(f"🚀 Executing mission: {args.directive}")

        # Create agent and run mission
        try:
            agent = ExecutiveAgent(agent_id="cli_agent", mcp_client=None)
            context = {
                "project": "cli_project",
                "session": "cli_session",
                "title": args.directive,
                "inputs": {
                    "code": args.code,
                    "user_context": args.context,
                },
                "risk_level": "medium", # Default risk level for CLI missions
            }
            result = asyncio.run(agent.execute_mission(args.directive, context))
            import json
            print("\n✅ Mission complete.")
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"❌ Error executing mission: {e}")
            sys.exit(1)
    else:
        # Run the desktop application
        try:
            import subprocess
            desktop_app_path = current_dir / "modern_desktop_app.py"
            if not desktop_app_path.exists():
                desktop_app_path = current_dir / "desktop_app.py"
            if not desktop_app_path.exists():
                print("❌ Could not find a desktop app script.")
                sys.exit(1)
            print("🚀 Starting Jarvis AI Desktop App...")
            subprocess.run([sys.executable, str(desktop_app_path)])
        except Exception as e:
            print(f"❌ Error starting application: {e}")
            sys.exit(1)

def run_indexer(args):
    """Rebuild repository index."""
    try:
        from tools.repository_indexer import RepositoryIndexer
        indexer = RepositoryIndexer()
        indexer.build_index(force_rebuild=args.force)
        print("✅ Repository index built")
    except Exception as e:  # pragma: no cover - runtime feedback
        print(f"❌ Error building index: {e}")
        sys.exit(1)

def show_version():
    """Show version information."""
    try:
        from jarvis_ai import __version__
        print(f"Jarvis AI v{__version__}")
        
        # Show additional info
        print(f"Python: {sys.version}")
        print(f"Platform: {sys.platform}")
        
        # Check for key dependencies
        deps = []
        try:
            import langchain
            deps.append(f"LangChain {langchain.__version__}")
        except ImportError:
            deps.append("LangChain: Not installed")
            
        try:
            import langgraph
            deps.append(f"LangGraph {langgraph.__version__}")
        except ImportError:
            deps.append("LangGraph: Not installed")
        
        print("Dependencies:")
        for dep in deps:
            print(f"  - {dep}")
            
    except Exception as e:
        print(f"❌ Error showing version: {e}")

if __name__ == "__main__":
    main()
