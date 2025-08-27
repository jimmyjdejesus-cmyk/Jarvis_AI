#!/usr/bin/env python3
"""
Quick test to verify the Cerebro backend integration works
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))


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
        if main_app.cerebro_orchestrator:
            result = await main_app.cerebro_orchestrator.coordinate_specialists(
                "Test security analysis of authentication system"
            )
            
            print(f"🎯 Test result:")
            print(f"   Type: {result.get('type')}")
            print(f"   Specialists used: {result.get('specialists_used')}")
            print(f"   Confidence: {result.get('confidence')}")
            print(f"   Response: {result.get('synthesized_response', '')[:100]}...")
            
            # Check if at least one specialist was used
            if result.get('specialists_used'):
                print("✅ Test PASSED: Specialist coordination successful.")
                return True
            else:
                print("❌ Test FAILED: No specialists were used.")
                return False
        else:
            print("❌ Cerebro orchestrator not initialized")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Cerebro: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_cerebro())
    if success:
        print("\n🎉 Cerebro integration test PASSED!")
        print("The backend is ready for the galaxy visualization.")
    else:
        print("\n💥 Cerebro integration test FAILED!")
        print("Check the backend setup.")
