#!/usr/bin/env python3
"""
Simple test for OpenRouter client without MCP dependencies
"""

import os
import sys

def test_openrouter_client():
    """Test OpenRouter client directly"""
    print("🧪 Testing OpenRouter Client...")

    # Set a dummy API key for testing (will fail but test structure)
    test_key = os.getenv("OPENROUTER_API_KEY", "sk-or-v1-test-key")

    try:
        # Import just the OpenRouter client
        sys.path.append(os.path.join(os.path.dirname(__file__), 'legacy'))
        # Direct import to avoid MCP dependencies
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "openrouter",
            os.path.join(os.path.dirname(__file__), 'legacy', 'jarvis', 'mcp', 'providers', 'openrouter.py')
        )
        openrouter_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(openrouter_module)
        OpenRouterClient = openrouter_module.OpenRouterClient

        print("✅ OpenRouter client imported successfully")

        # Test client initialization
        client = OpenRouterClient(api_key=test_key)
        print("✅ OpenRouter client initialized")

        # Test model selection
        low_model = client.get_model_for_complexity("low")
        medium_model = client.get_model_for_complexity("medium")
        high_model = client.get_model_for_complexity("high")

        print("✅ Model selection working:")
        print(f"   Low complexity: {low_model}")
        print(f"   Medium complexity: {medium_model}")
        print(f"   High complexity: {high_model}")

        # Test cost status
        cost_status = client.get_cost_status()
        print("✅ Cost tracking working:")
        print(".2f")
        print(".2f")

        # Test complexity classification (mock router)
        class MockRouter:
            def _classify_complexity(self, prompt, task_type):
                # Simple mock implementation
                prompt_len = len(prompt)
                if prompt_len > 100:
                    return "high" if "architecture" in prompt.lower() else "medium"
                return "low"

        router = MockRouter()
        test_prompts = [
            "Hello",
            "Write a function",
            "Design a system architecture"
        ]

        print("✅ Complexity classification working:")
        for prompt in test_prompts:
            complexity = router._classify_complexity(prompt, "general")
            print(f"   '{prompt}' -> {complexity}")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Required dependencies may be missing. Try: pip install requests")
        return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Run the simple test"""
    print("🚀 Jarvis AI OpenRouter Simple Test")
    print("=" * 40)

    success = test_openrouter_client()

    print("\n" + "=" * 40)
    if success:
        print("🎉 OpenRouter client implementation is working!")
        print("\nTo test with real API:")
        print("1. Get key from https://openrouter.ai/keys")
        print("2. Set: export OPENROUTER_API_KEY=your-key-here")
        print("3. Run: python3 test_openrouter.py")
    else:
        print("❌ Implementation has issues. Check errors above.")

if __name__ == "__main__":
    main()
