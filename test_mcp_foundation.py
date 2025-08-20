"""
Test MCP Foundation
"""
import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_mcp_foundation():
    """Test the MCP foundation components"""
    print("🧪 Testing MCP Foundation Components\n")
    
    try:
        # Test MCP Client
        print("1️⃣ Testing MCP Client...")
        from jarvis.mcp import MCPClient
        
        async with MCPClient() as client:
            # Test Ollama connection
            connected = await client.connect_to_server("ollama")
            print(f"   Ollama connection: {'✅ Success' if connected else '❌ Failed'}")
            
            if connected:
                models = await client.list_models("ollama")
                print(f"   Available models: {models}")
                
                # Test response generation
                try:
                    response = await client.generate_response("ollama", "llama3.2", "Hello, this is a test")
                    print(f"   Test response: {response[:100]}...")
                except Exception as e:
                    print(f"   Response generation failed: {e}")
        
        # Test Model Router
        print("\n2️⃣ Testing Model Router...")
        from jarvis.mcp import ModelRouter
        
        client = MCPClient()
        router = ModelRouter(client)
        
        # Test classification
        test_messages = [
            "Review this Python code: def hello(): print('world')",
            "What is the weather today?",
            "Generate a function to sort a list",
            "Analyze the security implications of this system"
        ]
        
        for msg in test_messages:
            classification = await router.classify_request(msg)
            print(f"   '{msg[:30]}...' → {classification['type']} ({classification['confidence']:.2f})")
        
        # Test Server Manager
        print("\n3️⃣ Testing Server Manager...")
        from jarvis.mcp import MCPServerManager
        
        server_manager = MCPServerManager(client)
        connections = await server_manager.initialize_all_servers()
        
        for server, success in connections.items():
            status = "✅ Connected" if success else "❌ Failed"
            print(f"   {server}: {status}")
        
        # Test MCP Agent
        print("\n4️⃣ Testing MCP Agent...")
        from jarvis.core.mcp_agent import MCPJarvisAgent
        
        agent = MCPJarvisAgent(enable_mcp=True)
        
        # Test basic functionality
        test_response = await agent.chat_async("Hello MCP Jarvis!")
        print(f"   MCP Agent response: {test_response[:100]}...")
        
        # Test capabilities
        capabilities = agent.get_capabilities()
        print(f"   Capabilities: {capabilities}")
        
        # Test status
        status = agent.get_mcp_status()
        print(f"   MCP Status: {status.get('enabled', False)}")
        
        print("\n✅ MCP Foundation Test Complete!")
        return True
        
    except Exception as e:
        print(f"\n❌ MCP Foundation Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_mcp_foundation())
    if success:
        print("\n🎉 MCP Foundation is ready!")
    else:
        print("\n⚠️  MCP Foundation needs attention")
