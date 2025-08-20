#!/usr/bin/env python3
"""
Test script for modern Jarvis architecture
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all modern Jarvis imports"""
    print("🧪 Testing Modern Jarvis Architecture...")
    
    # Test jarvis package
    try:
        import jarvis
        print("✅ jarvis package imported successfully")
        print(f"   Version: {jarvis.__version__}")
    except Exception as e:
        print(f"❌ jarvis package import failed: {e}")
        return False
    
    # Test individual components
    components = [
        ('DatabaseManager', 'jarvis.DatabaseManager'),
        ('SecurityManager', 'jarvis.SecurityManager'), 
        ('ModelClient', 'jarvis.ModelClient'),
        ('UIComponents', 'jarvis.UIComponents'),
        ('JarvisAgent', 'jarvis.JarvisAgent')
    ]
    
    all_success = True
    for name, attr_path in components:
        try:
            # Get attribute from jarvis package
            parts = attr_path.split('.')
            obj = jarvis
            for part in parts[1:]:
                obj = getattr(obj, part)
            
            if obj is not None:
                print(f"✅ {name} available")
            else:
                print(f"⚠️  {name} is None (fallback mode)")
        except Exception as e:
            print(f"❌ {name} failed: {e}")
            all_success = False
    
    return all_success

def test_legacy_fallback():
    """Test legacy fallback functionality"""
    print("\n🔄 Testing Legacy Fallback...")
    
    try:
        from database.database import get_user
        print("✅ Legacy database functions accessible")
    except Exception as e:
        print(f"❌ Legacy database fallback failed: {e}")
        return False
    
    try:
        import streamlit as st
        print("✅ Streamlit available")
    except Exception as e:
        print(f"❌ Streamlit not available: {e}")
        return False
    
    return True

def test_feature_detection():
    """Test feature detection logic"""
    print("\n🎯 Testing Feature Detection...")
    
    try:
        # Import the modern app logic
        import modern_app
        
        # Check if full features are detected
        features_available = True
        try:
            import jarvis
            features_available = all([
                jarvis.DatabaseManager is not None,
                jarvis.SecurityManager is not None,
                jarvis.ModelClient is not None,
                jarvis.UIComponents is not None,
                jarvis.JarvisAgent is not None
            ])
        except:
            features_available = False
        
        if features_available:
            print("✅ Full Feature Mode detected")
        else:
            print("⚠️  Basic Mode detected (some components unavailable)")
            
        return True
    except Exception as e:
        print(f"❌ Feature detection failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 MODERN JARVIS ARCHITECTURE TEST")
    print("=" * 60)
    
    success = True
    
    # Run tests
    success &= test_imports()
    success &= test_legacy_fallback() 
    success &= test_feature_detection()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED - Modern Architecture Working!")
    else:
        print("⚠️  SOME TESTS FAILED - Check output above")
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    main()
