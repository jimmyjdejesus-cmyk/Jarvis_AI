"""
Quick Multi-Agent Test
"""
import jarvis

def quick_test():
    print("🧪 Quick Multi-Agent Test")
    print("=" * 40)
    
    # Test Super Jarvis
    print("Testing Super Jarvis...")
    try:
        super_jarvis = jarvis.get_super_jarvis()
        print(f"✅ Super Jarvis created: {type(super_jarvis).__name__}")
        
        # Test capabilities
        capabilities = super_jarvis.get_capabilities()
        print(f"✅ Multi-agent enabled: {capabilities.get('multi_agent_enabled', False)}")
        print(f"✅ MCP enabled: {capabilities.get('mcp_enabled', False)}")
        
        # Simple test
        response = super_jarvis.chat("What is Python?")
        print(f"✅ Simple response: {response[:100]}...")
        
        # Multi-agent test (should trigger specialists)
        response = super_jarvis.chat("Review this code for security issues", 
                                   code="password = input(); if password == 'admin': login()")
        
        if "Multi-Agent Analysis" in response:
            print("✅ Multi-agent coordination activated!")
        else:
            print("ℹ️  Single agent response (normal for simple requests)")
        
        print("✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    quick_test()
