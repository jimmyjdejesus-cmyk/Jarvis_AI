#!/usr/bin/env python3
"""
Quick test to verify the Cerebro backend integration works
"""

import asyncio
import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))


@pytest.mark.asyncio
async def test_cerebro():
    print("🧠 Testing Cerebro Integration...")
    
    try:
        # Import the app module to access its globals
        import app.main as main_app
        
        # Initialize Cerebro
        await main_app.initialize_cerebro()
        
        print(f"✅ Cerebro initialized with {len(main_app.specialist_agents)} specialists")
        print(f"📋 Available specialists: {list(main_app.specialist_agents.keys())}")
        
        # Test orchestrator
        assert main_app.cerebro_orchestrator is not None, "Cerebro orchestrator not initialized"

        result = await main_app.cerebro_orchestrator.coordinate_specialists(
            "Test security analysis of authentication system",
        )

        print("🎯 Test result:")
        print(f"   Type: {result.get('type')}")
        print(f"   Specialists used: {result.get('specialists_used')}")
        print(f"   Confidence: {result.get('confidence')}")
        print(f"   Response: {result.get('synthesized_response', '')[:100]}...")

        assert result.get('specialists_used'), "No specialists were used."
            
    except Exception as e:
        pytest.fail(f"Error testing Cerebro: {e}")
