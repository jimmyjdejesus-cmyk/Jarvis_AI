#!/usr/bin/env python3
"""
Quick test to verify the Cerebro backend integration works
"""

import asyncio
import sys
import os
sys.path.insert(0, 'app')

async def test_cerebro():
    print("🧠 Testing Cerebro Integration...")
    
    try:
        from app.main import cerebro_orchestrator, specialist_agents, initialize_cerebro
        
        # Initialize Cerebro
        await initialize_cerebro()
        
        print(f"✅ Cerebro initialized with {len(specialist_agents)} specialists")
        print(f"📋 Available specialists: {list(specialist_agents.keys())}")
        
        # Test orchestrator
        if cerebro_orchestrator:
            result = await cerebro_orchestrator.coordinate_specialists(
                "Test security analysis of authentication system"
            )
            
            print(f"🎯 Test result:")
            print(f"   Type: {result.get('type')}")
            print(f"   Specialists used: {result.get('specialists_used')}")
            print(f"   Confidence: {result.get('confidence')}")
            print(f"   Response: {result.get('synthesized_response', '')[:100]}...")
            
            return True
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
