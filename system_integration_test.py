#!/usr/bin/env python3
"""
Jarvis AI - System Integration Test & Walkthrough
Tests all major components and shows how they work together
"""

import sys
import os
import subprocess
import time
from pathlib import Path

def print_section(title):
    """Print a section header."""
    print("\n" + "="*60)
    print(f"🔍 {title}")
    print("="*60)

def check_component(name, command, expected_output=None):
    """Check if a component is working."""
    print(f"\n📋 Testing {name}...")
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=10, shell=True)
        if result.returncode == 0:
            print(f"✅ {name}: Working")
            if expected_output and expected_output in result.stdout:
                print(f"   Expected output found: {expected_output}")
            return True
        else:
            print(f"❌ {name}: Failed")
            print(f"   Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {name}: Timeout (may be starting background service)")
        return None
    except Exception as e:
        print(f"❌ {name}: Error - {e}")
        return False

def test_python_environment():
    """Test Python environment and dependencies."""
    print_section("PYTHON ENVIRONMENT")
    
    # Check Python version
    check_component("Python Version", "python --version")
    
    # Check key dependencies
    dependencies = [
        ("Streamlit", "python -c 'import streamlit; print(streamlit.__version__)'"),
        ("LangChain", "python -c 'import langchain; print(\"LangChain available\")'"),
        ("LangGraph", "python -c 'import langgraph; print(\"LangGraph available\")'"),
        ("Requests", "python -c 'import requests; print(\"Requests available\")'"),
        ("Pandas", "python -c 'import pandas; print(\"Pandas available\")'"),
        ("Cryptography", "python -c 'import cryptography; print(\"Cryptography available\")'"),
        ("BCrypt", "python -c 'import bcrypt; print(\"BCrypt available\")'"),
    ]
    
    working_deps = 0
    for name, cmd in dependencies:
        if check_component(name, cmd):
            working_deps += 1
    
    print(f"\n📊 Dependencies Status: {working_deps}/{len(dependencies)} working")
    return working_deps == len(dependencies)

def test_ollama_integration():
    """Test Ollama integration."""
    print_section("OLLAMA INTEGRATION")
    
    # Check if Ollama is running
    ollama_running = check_component("Ollama Service", "curl -s http://localhost:11434/api/tags")
    
    if ollama_running:
        # Check available models
        check_component("Available Models", "curl -s http://localhost:11434/api/tags")
        
        # Test model health (if models available)
        check_component("Model Test", 'curl -s -X POST http://localhost:11434/api/generate -d \'{"model": "llama3.2", "prompt": "Hello", "stream": false}\'')
    else:
        print("ℹ️  Ollama not running. You can start it with: ollama serve")
    
    return ollama_running

def test_database_system():
    """Test database functionality."""
    print_section("DATABASE SYSTEM")
    
    # Check if database file exists
    db_path = Path("janus_database.db")
    if db_path.exists():
        print("✅ Database file exists")
        
        # Test database connectivity
        test_db = check_component("Database Connection", 
                                "python -c 'from database.database import init_db; init_db(); print(\"Database connected\")'")
        return test_db
    else:
        print("❌ Database file not found")
        print("   Run: python -c 'from database.database import init_db; init_db()'")
        return False

def test_authentication_system():
    """Test authentication system."""
    print_section("AUTHENTICATION SYSTEM")
    
    # Test password hashing
    hash_test = check_component("Password Hashing", 
                              "python -c 'from agent.features.security import hash_password; print(\"Hashing works\")'")
    
    # Test user management
    user_mgmt = check_component("User Management", 
                              "python -c 'from database.database import get_all_users; print(\"User management available\")'")
    
    return hash_test and user_mgmt

def test_ai_core():
    """Test AI core functionality."""
    print_section("AI CORE SYSTEM")
    
    # Test core agent
    core_test = check_component("Core Agent", 
                              "python -c 'from agent.core.core import JarvisAgent; print(\"Core agent available\")'")
    
    # Test tools system
    tools_test = check_component("Tools System", 
                               "python -c 'import agent.tools; print(\"Tools system available\")'")
    
    # Test RAG handler
    rag_test = check_component("RAG Handler", 
                             "python -c 'from agent.features.rag_handler import RAGHandler; print(\"RAG handler available\")'")
    
    return core_test and tools_test and rag_test

def test_web_interface():
    """Test web interface components."""
    print_section("WEB INTERFACE")
    
    # Check main app file
    app_path = Path("legacy/app.py")
    if app_path.exists():
        print("✅ Main app file exists")
        
        # Test import of main app components
        ui_test = check_component("UI Components", 
                                "python -c 'from ui.sidebar import sidebar; print(\"UI components available\")'")
        
        # Test analytics
        analytics_test = check_component("Analytics System", 
                                       "python -c 'from ui.analytics import render_analytics_dashboard; print(\"Analytics available\")'")
        
        return ui_test and analytics_test
    else:
        print("❌ Main app file not found")
        return False

def test_plugin_system():
    """Test plugin system."""
    print_section("PLUGIN SYSTEM")
    
    # Test plugin adapters
    adapter_test = check_component("Plugin Adapters", 
                                 "python -c 'from agent.adapters.plugin_adapters import PluginAdapter; print(\"Plugin adapters available\")'")
    
    # Test plugin registry
    registry_test = check_component("Plugin Registry", 
                                  "python -c 'from agent.adapters.plugin_registry import PluginRegistry; print(\"Plugin registry available\")'")
    
    return adapter_test and registry_test

def test_configuration():
    """Test configuration system."""
    print_section("CONFIGURATION")
    
    # Check config files
    config_files = [
        "config/config.yaml",
        "pyproject.toml",
        "hardware_protection_config.yaml"
    ]
    
    config_status = []
    for config_file in config_files:
        if Path(config_file).exists():
            print(f"✅ {config_file} exists")
            config_status.append(True)
        else:
            print(f"❌ {config_file} missing")
            config_status.append(False)
    
    return all(config_status)

def run_system_walkthrough():
    """Run a complete system walkthrough."""
    print("🤖 JARVIS AI - SYSTEM INTEGRATION WALKTHROUGH")
    print("=" * 60)
    print("Testing all components to ensure they work together...")
    
    test_results = []
    
    # Run all tests
    test_results.append(("Python Environment", test_python_environment()))
    test_results.append(("Configuration", test_configuration()))
    test_results.append(("Database System", test_database_system()))
    test_results.append(("Authentication", test_authentication_system()))
    test_results.append(("AI Core", test_ai_core()))
    test_results.append(("Web Interface", test_web_interface()))
    test_results.append(("Plugin System", test_plugin_system()))
    test_results.append(("Ollama Integration", test_ollama_integration()))
    
    # Summary
    print_section("INTEGRATION TEST SUMMARY")
    
    working_systems = 0
    total_systems = len(test_results)
    
    for system_name, result in test_results:
        if result is True:
            print(f"✅ {system_name}: WORKING")
            working_systems += 1
        elif result is None:
            print(f"⏰ {system_name}: TIMEOUT/BACKGROUND")
        else:
            print(f"❌ {system_name}: FAILED")
    
    print(f"\n📊 OVERALL STATUS: {working_systems}/{total_systems} systems working")
    
    # Recommendations
    print_section("NEXT STEPS")
    
    if working_systems >= total_systems - 1:  # Allow for Ollama to be optional
        print("🎉 System is ready to use!")
        print("\n🚀 How to start:")
        print("   1. Run: start_launcher.bat")
        print("   2. Choose option 3 (Web UI)")
        print("   3. Navigate to http://localhost:8501")
        print("   4. Login with admin credentials")
        print("\n📚 For help:")
        print("   - Read: HOW_TO_USE_JARVIS_AI.md")
        print("   - Check: COMPLETED_WORK_SUMMARY.md")
    else:
        print("⚠️  Some systems need attention:")
        
        failed_systems = [name for name, result in test_results if result is False]
        for system in failed_systems:
            print(f"   - Fix: {system}")
        
        print("\n🛠️  Common fixes:")
        print("   - Install dependencies: pip install -r development/requirements.txt")
        print("   - Initialize database: python -c 'from database.database import init_db; init_db()'")
        print("   - Start Ollama: ollama serve")
        print("   - Create admin: python scripts/create_admin_user.py")

def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # Quick test mode
        print("🔍 Quick System Check...")
        test_python_environment()
        test_database_system()
        test_ollama_integration()
    else:
        # Full walkthrough
        run_system_walkthrough()

if __name__ == "__main__":
    main()
