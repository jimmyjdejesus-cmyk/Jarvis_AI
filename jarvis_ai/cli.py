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
    
    # Run command to start the application
    run_parser = subparsers.add_parser("run", help="Start the Jarvis AI application")
    run_parser.add_argument("--port", type=int, default=8501, help="Port to run on (default: 8501)")
    run_parser.add_argument("--host", default="localhost", help="Host to bind to (default: localhost)")
    run_parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    
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
    """Run the Jarvis AI application."""
    try:
        import streamlit.web.cli as stcli
        import streamlit as st
        
        # Determine the app file to run
        app_file = None
        possible_locations = [
            current_dir / "legacy" / "app.py",
            current_dir / "app.py",
            current_dir / "legacy" / "streamlit_app.py"
        ]
        
        for location in possible_locations:
            if location.exists():
                app_file = str(location)
                break
        
        if not app_file:
            print("❌ Could not find main application file")
            print("Looking for app.py in:", [str(p) for p in possible_locations])
            sys.exit(1)
        
        print(f"🚀 Starting Jarvis AI on {args.host}:{args.port}")
        print(f"📁 Using app file: {app_file}")
        
        # Build streamlit command args
        sys.argv = [
            "streamlit",
            "run",
            app_file,
            "--server.port", str(args.port),
            "--server.address", args.host,
        ]
        
        if args.headless:
            sys.argv.extend([
                "--server.headless", "true",
                "--server.enableCORS", "false",
                "--server.enableXsrfProtection", "false"
            ])
        
        # Run streamlit
        stcli.main()
        
    except ImportError:
        print("❌ Streamlit not found. Please install dependencies:")
        print("   pip install jarvis-ai")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

def manage_config(args):
    """Manage configuration."""
    try:
        from legacy.agent.core.config_manager import get_config_manager
        # Dynamically import get_config_manager from legacy.agent.core.config_manager
        config_manager_path = current_dir / "legacy" / "agent" / "core" / "config_manager.py"
        spec = importlib.util.spec_from_file_location("config_manager", str(config_manager_path))
        config_manager_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_manager_module)
        get_config_manager = config_manager_module.get_config_manager
        config_manager = get_config_manager()
        
        if args.show:
            config = config_manager.load_config()
            print("📋 Current Jarvis AI Configuration:")
            print(f"   Version: {config.version}")
            print(f"   Debug Mode: {config.debug_mode}")
            print(f"   Data Directory: {config.data_directory}")
            print(f"   Logs Directory: {config.logs_directory}")
            print(f"   Ollama Endpoint: {config.integrations.ollama_endpoint}")
            print(f"   Default Model: {config.integrations.default_model}")
            print(f"   LangSmith Enabled: {config.lang_ecosystem.langsmith.enabled}")
            print(f"   LangSmith API Key: {'Set' if config.lang_ecosystem.langsmith.api_key else 'Not set'}")
            print(f"   V2 Enabled: {config.v2.enabled}")
            print(f"   V2 Expert Model: {config.v2.expert_model}")
            
        elif args.validate:
            try:
                config = config_manager.load_config()
                print("✅ Configuration is valid")
            except Exception as e:
                print(f"❌ Configuration validation failed: {e}")
                sys.exit(1)
                
        elif args.init:
            print("🔧 Initializing default configuration...")
            # Copy example config if it exists
            config_dir = Path.cwd() / "config"
            config_dir.mkdir(exist_ok=True)
            
            example_config = current_dir / "legacy" / "config" / "config.example.yaml"
            target_config = config_dir / "config.yaml"
            
            if example_config.exists() and not target_config.exists():
                import shutil
                shutil.copy2(example_config, target_config)
                print(f"✅ Configuration initialized at {target_config}")
                print("   Please edit the configuration file to customize settings")
            else:
                print("❌ Could not initialize configuration")
                print(f"   Example config: {example_config}")
                print(f"   Target config: {target_config}")
        else:
            print("Use --show, --validate, or --init with config command")
            
    except Exception as e:
        print(f"❌ Error managing configuration: {e}")
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
            import streamlit
            deps.append(f"Streamlit {streamlit.__version__}")
        except ImportError:
            deps.append("Streamlit: Not installed")
            
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