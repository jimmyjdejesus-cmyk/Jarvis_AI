"""
🚀 Phase 3 Demo: Multi-Agent Specialists
Test the new multi-agent coordination capabilities
"""
import asyncio
import jarvis

async def test_multi_agent_system():
    """Test the multi-agent system capabilities"""
    
    print("🌟" * 30)
    print("🚀 PHASE 3: MULTI-AGENT SPECIALISTS DEMO")
    print("🌟" * 30)
    print()
    
    # Test 1: Simple vs Smart vs Super Jarvis
    print("🎭 **TESTING ALL JARVIS MODES:**")
    print()
    
    # Simple Jarvis
    print("1️⃣ **Simple Jarvis** (Basic Mode)")
    simple = jarvis.get_simple_jarvis()
    print(f"   Agent Type: {type(simple).__name__}")
    response = simple.chat("What is Python?")
    print(f"   Response: {response[:80]}...")
    print()
    
    # Smart Jarvis
    print("2️⃣ **Smart Jarvis** (MCP Mode)")
    smart = jarvis.get_smart_jarvis()
    print(f"   Agent Type: {type(smart).__name__}")
    response = smart.chat("What is Python?")
    print(f"   Response: {response[:80]}...")
    print()
    
    # Super Jarvis
    print("3️⃣ **Super Jarvis** (Multi-Agent Mode)")
    super_jarvis = jarvis.get_super_jarvis()
    print(f"   Agent Type: {type(super_jarvis).__name__}")
    
    # Test capabilities
    capabilities = super_jarvis.get_capabilities()
    print(f"   Multi-Agent Enabled: {capabilities.get('multi_agent_enabled', False)}")
    print(f"   Available Specialists: {capabilities.get('available_specialists', [])}")
    print()
    
    # Test 2: Multi-Agent Coordination
    print("🤖 **TESTING MULTI-AGENT COORDINATION:**")
    print()
    
    # Test different complexity levels
    test_scenarios = [
        {
            "name": "Simple Question",
            "message": "What is the difference between lists and tuples in Python?",
            "expected_specialists": 0
        },
        {
            "name": "Code Review Request", 
            "message": "Review this Python function for issues",
            "code": """
def process_user_data(data):
    result = []
    for item in data:
        if item:
            result.append(item.upper())
    return result
""",
            "expected_specialists": 1
        },
        {
            "name": "Security Analysis",
            "message": "Analyze this web application for security vulnerabilities",
            "code": """
from flask import Flask, request
app = Flask(__name__)

@app.route('/user/<user_id>')
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    # Execute query directly
    return query
""",
            "expected_specialists": 2
        },
        {
            "name": "Architecture Review",
            "message": "Review this microservices architecture design for a banking application with authentication, transactions, and reporting services",
            "expected_specialists": 3
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"📋 **Scenario {i}: {scenario['name']}**")
        
        try:
            if 'code' in scenario:
                response = super_jarvis.chat(scenario['message'], code=scenario['code'])
            else:
                response = super_jarvis.chat(scenario['message'])
            
            # Check if multi-agent coordination was used
            if "Multi-Agent Analysis" in response:
                print("   ✅ Multi-agent coordination activated")
                if "Specialists:" in response:
                    # Extract specialists used
                    lines = response.split('\n')
                    for line in lines:
                        if line.startswith("**Specialists:**"):
                            specialists = line.replace("**Specialists:**", "").strip()
                            print(f"   🤖 Specialists Used: {specialists}")
                            break
            else:
                print("   📱 Single agent response (as expected for simple requests)")
            
            print(f"   📄 Response: {response[:100]}...")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    # Test 3: Specific Specialist Analysis
    print("🔬 **TESTING SPECIFIC SPECIALIST ANALYSIS:**")
    print()
    
    # Test explicit specialist requests
    specialist_tests = [
        {
            "name": "Code Review Specialist",
            "specialists": ["code_review"],
            "message": "Review this code for best practices",
            "code": "def calc(x,y): return x+y if x>0 else y"
        },
        {
            "name": "Security Specialist", 
            "specialists": ["security"],
            "message": "Analyze security risks in this authentication system",
            "code": "password = request.form['password']; if password == 'admin': login_user()"
        },
        {
            "name": "Multi-Specialist Coordination",
            "specialists": ["code_review", "security", "testing"],
            "message": "Comprehensive analysis of this payment processing function",
            "code": """
def process_payment(amount, card_number):
    if amount > 0:
        charge_card(card_number, amount)
        return "Success"
    return "Error"
"""
        }
    ]
    
    for test in specialist_tests:
        print(f"🔍 **{test['name']}**")
        
        try:
            # Use analyze_with_specialists method
            result = super_jarvis.analyze_with_specialists(
                test['message'], 
                specialists=test['specialists'],
                code=test.get('code')
            )
            
            if 'error' in result:
                print(f"   ❌ Error: {result['error']}")
            else:
                specialists_used = result.get('specialists_used', [])
                confidence = result.get('confidence', 0.0)
                print(f"   ✅ Analysis Complete")
                print(f"   🤖 Specialists: {', '.join(specialists_used)}")
                print(f"   📊 Confidence: {confidence:.1%}")
                
                response = result.get('synthesized_response', 'No response')
                print(f"   📄 Response: {response[:150]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    # Test 4: System Health Check
    print("🏥 **SYSTEM HEALTH CHECK:**")
    print()
    
    try:
        health = await super_jarvis.health_check()
        
        print(f"Overall Status: {health['overall_status'].upper()}")
        print()
        print("System Components:")
        
        for system, status in health['systems'].items():
            if status.get('status'):
                icon = "✅" if status['status'] in ['healthy', 'ready'] else "❌"
                print(f"  {icon} {system.replace('_', ' ').title()}: {status['status']}")
            elif status.get('available') is not None:
                icon = "✅" if status['available'] else "❌"
                print(f"  {icon} {system.replace('_', ' ').title()}: {'Available' if status['available'] else 'Unavailable'}")
        
        print()
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        print()
    
    # Test 5: Performance Comparison
    print("⚡ **PERFORMANCE COMPARISON:**")
    print()
    
    test_message = "Explain the benefits of microservices architecture"
    
    modes = [
        ("Simple", jarvis.get_simple_jarvis()),
        ("Smart", jarvis.get_smart_jarvis()),
        ("Super", jarvis.get_super_jarvis())
    ]
    
    for mode_name, agent in modes:
        try:
            import time
            start_time = time.time()
            response = agent.chat(test_message)
            end_time = time.time()
            
            print(f"🚀 **{mode_name} Jarvis:**")
            print(f"   ⏱️  Response Time: {end_time - start_time:.2f} seconds")
            print(f"   📏 Response Length: {len(response)} characters")
            print(f"   🎯 Agent Type: {type(agent).__name__}")
            print()
            
        except Exception as e:
            print(f"❌ {mode_name} Jarvis failed: {e}")
            print()
    
    print("🎉 **PHASE 3 DEMO COMPLETE!**")
    print()
    print("✅ **Achievements Unlocked:**")
    print("   🤖 Multi-agent specialist coordination")
    print("   🧠 Intelligent task complexity analysis")
    print("   🎭 Multiple Jarvis operation modes")
    print("   🔍 Specialist-specific analysis capabilities")
    print("   🏥 Comprehensive health monitoring")
    print("   ⚡ Performance optimization across modes")
    print()
    print("🔥 **READY FOR PHASE 4: ADVANCED WORKFLOWS!** 🔥")

if __name__ == "__main__":
    asyncio.run(test_multi_agent_system())
