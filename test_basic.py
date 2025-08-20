#!/usr/bin/env python3
"""
Basic test to isolate the hanging issue
"""

print("🚀 Basic Test Starting...")

import os
from pathlib import Path

print("✅ Basic imports successful")

# Load environment variables from .env file
def load_env():
    env_file = Path('.env')
    if env_file.exists():
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

print("Loading environment...")
load_env()
print("✅ Environment loaded")

print("Testing LangSmith import...")
try:
    from langsmith import Client
    print("✅ LangSmith import successful")
    
    print("Creating client...")
    client = Client()
    print("✅ Client created")
    
    print("Listing projects...")
    projects = list(client.list_projects(limit=1))
    print(f"✅ Found {len(projects)} project(s)")
    
except Exception as e:
    print(f"❌ LangSmith failed: {e}")

print("✅ Test completed!")
