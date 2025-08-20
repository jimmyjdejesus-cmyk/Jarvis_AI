"""
Test Enhanced Jarvis Interface
"""
import jarvis

def test_enhanced_interface():
    print('🚀 Testing Enhanced Jarvis Interface')
    print('=' * 50)

    # Test simple mode
    print('1️⃣ Simple Jarvis:')
    simple = jarvis.get_simple_jarvis()
    print(f'   Type: {type(simple)}')
    response = simple.chat('Hello simple Jarvis!')
    print(f'   Response: {response[:80]}...')

    # Test smart mode (MCP)
    print('\n2️⃣ Smart Jarvis (MCP):')
    smart = jarvis.get_smart_jarvis()
    print(f'   Type: {type(smart)}')
    response = smart.chat('Hello smart Jarvis!')
    print(f'   Response: {response[:80]}...')

    # Test capabilities
    print('\n3️⃣ Smart Jarvis Capabilities:')
    capabilities = smart.get_capabilities()
    print(f'   MCP Enabled: {capabilities["mcp_enabled"]}')
    print(f'   MCP Initialized: {capabilities["mcp_initialized"]}')
    print(f'   Healthy Servers: {capabilities.get("healthy_servers", [])}')

    # Test auto mode
    print('\n4️⃣ Auto Jarvis (default):')
    auto = jarvis.get_jarvis_agent()
    print(f'   Type: {type(auto)}')
    status = auto.get_mcp_status()
    print(f'   MCP Enabled: {status.get("enabled", False)}')

    print('\n✅ Enhanced Jarvis Interface Working!')
    return True

if __name__ == "__main__":
    test_enhanced_interface()
