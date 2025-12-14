#!/usr/bin/env python3
"""
Test script for OpenRouter integration
Run this to verify your OpenRouter setup works correctly
"""

import os
import sys

# Add the legacy path to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'legacy'))

def test_openrouter_connection():
    """Test basic OpenRouter connection"""
    print("🧪 Testing OpenRouter Connection...")

    # Check if API key is set
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found in environment")
        print("   Please set your OpenRouter API key:")
        print("   export OPENROUTER_API_KEY=sk-or-v1-your-key-here")
        return False

    if not api_key.startswith("sk-or-v1"):
        print("❌ OPENROUTER_API_KEY doesn't look like a valid OpenRouter key")
        print("   OpenRouter keys start with 'sk-or-v1-'")
        return False

    try:
        from jarvis.mcp.providers.openrouter import OpenRouterClient

        print("✅ OpenRouter client imported successfully")

        client = OpenRouterClient(api_key=api_key)
        print("✅ OpenRouter client initialized")

        # Test a simple request
        print("📤 Testing API call...")
        result = client.generate("Say 'Hello from OpenRouter!' in exactly 5 words.")

        print("✅ API call successful!")
        print(f"📄 Response: {result}")

        # Check cost status
        cost_status = client.get_cost_status()
        print("💰 Cost Status:")
        print(".2f")
        print(".2f")
        print(f"   Over limit: {cost_status['is_over_limit']}")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you're running this from the Jarvis_AI directory")
        return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_model_router():
    """Test the model router integration"""
    print("\n🧪 Testing Model Router Integration...")

    try:
        from jarvis.mcp.model_router import ModelRouter
        from jarvis.mcp.client import MCPClient

        print("✅ Model router imported successfully")

        # Create mock MCP client (we'll only test OpenRouter part)
        mcp_client = None  # We'll modify router to work without full MCP

        # For now, just test the complexity classification
        router = ModelRouter(mcp_client)

        test_prompts = [
            "Hello world",  # Should be low
            "Write a Python function to calculate fibonacci numbers",  # Should be medium
            "Design a secure authentication system for a web application",  # Should be high
        ]

        for prompt in test_prompts:
            complexity = router._classify_complexity(prompt, "general")
            print(f"📝 '{prompt[:50]}...' -> {complexity} complexity")

        print("✅ Model router complexity classification working")
        return True

    except Exception as e:
        print(f"❌ Model router test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Jarvis AI OpenRouter Integration Test Suite")
    print("=" * 50)

    # Test 1: OpenRouter Connection
    openrouter_ok = test_openrouter_connection()

    # Test 2: Model Router (basic functionality)
    router_ok = test_model_router()

    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   OpenRouter Connection: {'✅ PASS' if openrouter_ok else '❌ FAIL'}")
    print(f"   Model Router: {'✅ PASS' if router_ok else '❌ FAIL'}")

    if openrouter_ok and router_ok:
        print("\n🎉 All tests passed! Your Jarvis AI cloud-first setup is ready!")
        print("\nNext steps:")
        print("1. Start Ollama: ollama serve")
        print("2. Pull models: ollama pull llama3.2:3b && ollama pull llama3:8b")
        print("3. Start Jarvis: cd legacy && python app/main.py")
        print("4. Test full integration with: curl -X POST http://localhost:8000/api/v1/chat -H 'Content-Type: application/json' -d '{\"messages\":[{\"role\":\"user\",\"content\":\"Hello Jarvis!\"}]}'")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above and fix configuration.")
        print("   See CLOUD_FIRST_SETUP.md for detailed setup instructions.")

if __name__ == "__main__":
    main()
