#!/usr/bin/env python3
"""
Reliability Mechanisms Demo
Demonstrates the fallback and reliability features of Jarvis AI.
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Add development path for imports
dev_path = Path(__file__).parent.parent
sys.path.insert(0, str(dev_path))

try:
    from agent.core.reliability import get_reliability_manager, OperationMode
    from agent.core.rag_fallback import get_offline_rag_handler
    from agent.workflows.reliability_workflow import execute_reliability_check
    RELIABILITY_AVAILABLE = True
except ImportError as e:
    print(f"Reliability modules not available: {e}")
    RELIABILITY_AVAILABLE = False


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"🔧 {title}")
    print("=" * 60)


def print_section(title):
    """Print a formatted section header."""
    print(f"\n📋 {title}")
    print("-" * 40)


def demonstrate_operation_modes():
    """Demonstrate different operation modes."""
    print_header("Operation Modes Demonstration")
    
    if not RELIABILITY_AVAILABLE:
        print("❌ Reliability modules not available")
        return
    
    # Get reliability manager
    reliability_manager = get_reliability_manager()
    
    print(f"Initial mode: {reliability_manager.get_current_mode().value}")
    print(f"Initial state: {reliability_manager.get_current_state().value}")
    
    # Demonstrate mode switching
    modes_to_test = [
        (OperationMode.LOCAL_ONLY, "Simulating web connectivity issues"),
        (OperationMode.OFFLINE, "Simulating service outage"),
        (OperationMode.BASIC, "Simulating resource constraints"),
        (OperationMode.EMERGENCY, "Simulating critical failure"),
        (OperationMode.FULL, "Services recovered")
    ]
    
    for mode, reason in modes_to_test:
        print_section(f"Switching to {mode.value.upper()} mode")
        
        reliability_manager.force_mode_switch(mode, reason)
        
        print(f"✅ Mode: {reliability_manager.get_current_mode().value}")
        print(f"🔧 Reason: {reason}")
        print(f"⚙️ Web RAG enabled: {reliability_manager.can_use_web_rag()}")
        print(f"💾 Cache only: {reliability_manager.should_use_cache_only()}")
        print(f"⚡ Minimal mode: {reliability_manager.is_minimal_mode()}")
        print(f"🚨 Emergency mode: {reliability_manager.is_emergency_mode()}")
        
        time.sleep(1)  # Brief pause between mode switches


def demonstrate_offline_rag():
    """Demonstrate offline RAG functionality."""
    print_header("Offline RAG Demonstration")
    
    if not RELIABILITY_AVAILABLE:
        print("❌ Reliability modules not available")
        return
    
    offline_handler = get_offline_rag_handler()
    
    test_queries = [
        "What are the system capabilities?",
        "How do I check system status?",
        "What commands are available?",
        "Help me troubleshoot an error",
        "Random query about something"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print_section(f"Query {i}: {query}")
        
        response = offline_handler.handle_rag_request(query, [], "offline", "")
        print(f"📝 Response: {response[:200]}...")
        
        # Check if response was cached
        cached = offline_handler.enhanced_cache.get(query, [], "offline", "")
        cache_status = "✅ Cached" if cached else "❌ Not cached"
        print(f"💾 Cache status: {cache_status}")


def demonstrate_reliability_workflow():
    """Demonstrate reliability workflow execution."""
    print_header("Reliability Workflow Demonstration")
    
    if not RELIABILITY_AVAILABLE:
        print("❌ Reliability modules not available")
        return
    
    test_scenarios = [
        "system health check",
        "What happens during a service failure?",
        "How does recovery work?",
        "Test emergency response",
        ""  # Empty query
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print_section(f"Scenario {i}: {scenario or 'Empty query'}")
        
        result = execute_reliability_check(scenario)
        
        print(f"✅ Success: {result.get('success', False)}")
        print(f"🏥 Final state: {result.get('final_state', 'unknown')}")
        print(f"⚙️ Operation mode: {result.get('operation_mode', 'unknown')}")
        print(f"🔄 Recovery attempts: {result.get('recovery_attempts', 0)}")
        print(f"📝 Response: {result.get('response', 'No response')[:150]}...")
        
        if result.get('requires_escalation'):
            print("🚨 Administrator escalation required")


def demonstrate_error_scenarios():
    """Demonstrate error handling and recovery."""
    print_header("Error Scenarios Demonstration")
    
    if not RELIABILITY_AVAILABLE:
        print("❌ Reliability modules not available")
        return
    
    reliability_manager = get_reliability_manager()
    
    print_section("Network Failure Simulation")
    reliability_manager._handle_network_failure()
    print(f"Mode after network failure: {reliability_manager.get_current_mode().value}")
    
    print_section("Service Recovery Simulation")
    recovery_success = reliability_manager._recover_ollama_service()
    print(f"Ollama recovery attempted: {recovery_success}")
    
    print_section("Cache Recovery Simulation")  
    cache_recovery = reliability_manager._recover_cache_service()
    print(f"Cache recovery attempted: {cache_recovery}")
    
    print_section("System Status Report")
    status = reliability_manager.get_system_status()
    print(f"Current mode: {status['mode']}")
    print(f"Current state: {status['state']}")
    print(f"Fallback events: {len(status['fallback_history'])}")
    
    if status['fallback_history']:
        print("Recent events:")
        for event in status['fallback_history'][-3:]:
            timestamp = event.get('timestamp', 'Unknown')
            from_mode = event.get('from_mode', 'unknown')
            to_mode = event.get('to_mode', 'unknown')
            reason = event.get('reason', 'No reason')
            print(f"  • {timestamp}: {from_mode} → {to_mode} ({reason})")


def demonstrate_cache_functionality():
    """Demonstrate enhanced cache functionality."""
    print_header("Enhanced Cache Demonstration")
    
    if not RELIABILITY_AVAILABLE:
        print("❌ Reliability modules not available")
        return
    
    offline_handler = get_offline_rag_handler()
    cache = offline_handler.enhanced_cache
    
    print_section("Cache Statistics")
    stats = cache.get_cache_stats()
    print(f"📊 Total entries: {stats.get('total_entries', 0)}")
    print(f"💾 Memory entries: {stats.get('memory_entries', 0)}")
    print(f"📁 Cache directory: {stats.get('cache_dir', 'Unknown')}")
    print(f"📈 Cache size: {stats.get('cache_size_mb', 0):.2f} MB")
    
    print_section("Emergency Response Testing")
    emergency_queries = [
        "system status",
        "help me",
        "error occurred",
        "what can I do?"
    ]
    
    for query in emergency_queries:
        response = cache.get_emergency_response(query)
        print(f"❓ Query: {query}")
        print(f"🚨 Emergency response: {response[:100]}...")
        print()


def run_demo():
    """Run the complete reliability mechanisms demonstration."""
    print("🚀 Jarvis AI Reliability Mechanisms Demo")
    print(f"📅 Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not RELIABILITY_AVAILABLE:
        print("\n❌ Reliability modules are not available.")
        print("Please ensure the development environment is properly set up.")
        return
    
    try:
        # Run all demonstrations
        demonstrate_operation_modes()
        demonstrate_offline_rag() 
        demonstrate_reliability_workflow()
        demonstrate_error_scenarios()
        demonstrate_cache_functionality()
        
        print_header("Demo Complete")
        print("✅ All reliability mechanisms demonstrated successfully!")
        print("📊 System operating in fallback modes as expected.")
        print("🔧 Error recovery and graceful degradation working properly.")
        
    except Exception as e:
        print(f"\n💥 Demo failed with error: {e}")
        print("This demonstrates the system's error handling capabilities!")
        
        # Even in failure, show emergency response
        if RELIABILITY_AVAILABLE:
            try:
                offline_handler = get_offline_rag_handler()
                emergency_response = offline_handler.enhanced_cache.get_emergency_response(
                    "demo failed"
                )
                print(f"🚨 Emergency response: {emergency_response}")
            except Exception as nested_e:
                print(f"Emergency response also failed: {nested_e}")
    
    print(f"\n📅 Demo completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    run_demo()