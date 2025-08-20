#!/usr/bin/env python3
"""
Check Jarvis Components Status
"""

import jarvis

def check_components():
    print("🔍 JARVIS COMPONENTS STATUS")
    print("=" * 50)
    print(f"📦 Package Version: {jarvis.__version__}")
    print()
    
    print("📋 Available Components:")
    components = [
        ("🗄️  DatabaseManager", jarvis.DatabaseManager),
        ("🔒 SecurityManager", jarvis.SecurityManager), 
        ("🤖 JarvisAgent", jarvis.JarvisAgent),
        ("📊 ModelClient", jarvis.ModelClient),
        ("🎨 UIComponents", jarvis.UIComponents)
    ]
    
    for name, component in components:
        status = "✅ Available" if component is not None else "❌ Not Available"
        print(f"{name}: {status}")
    
    print()
    print("🧪 Testing Component Initialization:")
    
    # Test Database Manager
    try:
        db = jarvis.get_database_manager()
        print("✅ Database Manager: Initialized")
        users = db.get_all_users()
        print(f"   Users in database: {len(users)}")
    except Exception as e:
        print(f"❌ Database Manager: {e}")
    
    # Test Security Manager
    try:
        sec = jarvis.get_security_manager()
        print("✅ Security Manager: Initialized")
        security_info = sec.get_security_info()
        print(f"   Rate limits active: {security_info['active_rate_limits']}")
    except Exception as e:
        print(f"❌ Security Manager: {e}")
    
    # Test Jarvis Agent
    try:
        agent = jarvis.get_jarvis_agent()
        print("✅ Jarvis Agent: Initialized")
        print(f"   Model: {agent.model_name}")
        print(f"   Base URL: {agent.base_url}")
        
        # Test service availability
        available = agent.is_available()
        status = "🟢 Online" if available else "🔴 Offline"
        print(f"   AI Service: {status}")
        
        if available:
            models = agent.get_available_models()
            print(f"   Available models: {len(models)}")
            if models:
                print(f"   Models: {', '.join(models[:3])}{'...' if len(models) > 3 else ''}")
        
    except Exception as e:
        print(f"❌ Jarvis Agent: {e}")
    
    print()
    print("📊 Summary:")
    working_components = sum(1 for _, comp in components if comp is not None)
    print(f"Working Components: {working_components}/{len(components)}")
    
    if working_components >= 3:  # DB, Security, Agent are core
        print("🚀 Status: Full Feature Mode")
    else:
        print("⚠️  Status: Limited Mode")

if __name__ == "__main__":
    check_components()
