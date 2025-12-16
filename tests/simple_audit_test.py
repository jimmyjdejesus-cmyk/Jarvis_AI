#!/usr/bin/env python3
"""
Simple test for the Jarvis AI audit system core components.
"""

import sys
from pathlib import Path

# Add the jarvis_core directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "jarvis_core"))

def test_imports():
    """Test that all audit modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        from audit.models import AuditFinding, AuditReport, ScanConfiguration, AuditCategory, SeverityLevel
        print("✅ Models imported successfully")
        
        from audit.scanner import SecurityScanner, CodeQualityScanner, DependencyScanner
        print("✅ Scanners imported successfully")
        
        from audit.engine import AuditEngine
        print("✅ AuditEngine imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_models():
    """Test that models can be instantiated."""
    print("\n🧪 Testing model instantiation...")
    
    try:
        from audit.models import AuditFinding, AuditReport, ScanConfiguration, AuditCategory, SeverityLevel
        
        # Test AuditFinding
        finding = AuditFinding(
            id="test_001",
            category=AuditCategory.SECURITY,
            severity=SeverityLevel.HIGH,
            title="Test Finding",
            description="Test description",
            file_path="test.py",
            line_number=1,
            remediation="Fix this"
        )
        print(f"✅ AuditFinding created: {finding.title}")
        
        # Test ScanConfiguration
        config = ScanConfiguration()
        print(f"✅ ScanConfiguration created with {len(config.exclude_patterns)} exclude patterns")
        
        return True
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_scanners():
    """Test that scanners can be instantiated."""
    print("\n🧪 Testing scanner instantiation...")
    
    try:
        from audit.models import ScanConfiguration
        from audit.scanner import SecurityScanner, CodeQualityScanner, DependencyScanner
        
        config = ScanConfiguration()
        
        # Test scanner instantiation
        security_scanner = SecurityScanner(config)
        quality_scanner = CodeQualityScanner(config)
        dep_scanner = DependencyScanner(config)
        
        print("✅ All scanners instantiated successfully")
        
        # Test with minimal file content
        test_content = '''
def test_function():
    password = "hardcoded_secret"
    return password

# TODO: fix this function
def complex_function():
    for i in range(100):
        if i > 50:
            return i
        elif i == 25:
            print("magic number 25")
        elif i == 75:
            print("another magic number 75")
        else:
            continue
'''
        
        test_file = Path("/tmp/test_audit.py")
        test_file.write_text(test_content)
        
        # Test security scanner
        security_findings = security_scanner.scan_files([test_file])
        print(f"🔒 Security scanner found {len(security_findings)} issues")
        
        # Test quality scanner  
        quality_findings = quality_scanner.scan_files([test_file])
        print(f"📝 Quality scanner found {len(quality_findings)} issues")
        
        # Clean up
        test_file.unlink()
        
        return True
    except Exception as e:
        print(f"❌ Scanner test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_engine():
    """Test that the audit engine can be instantiated."""
    print("\n🧪 Testing audit engine...")
    
    try:
        from audit.models import ScanConfiguration
        from audit.engine import AuditEngine
        
        config = ScanConfiguration()
        engine = AuditEngine(config)
        
        print("✅ AuditEngine instantiated successfully")
        
        # Test scan status
        status = engine.get_scan_status()
        print(f"✅ Scan status: {status['scan_in_progress']}")
        
        return True
    except Exception as e:
        print(f"❌ Engine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Starting Simple Jarvis AI Audit System Tests")
    print("="*80)
    
    # Run all tests
    tests = [
        ("Import Test", test_imports),
        ("Model Test", test_models), 
        ("Scanner Test", test_scanners),
        ("Engine Test", test_engine)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        success = test_func()
        results.append((test_name, success))
    
    print("\n" + "="*80)
    print("🏁 TEST SUMMARY")
    print("="*80)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All core tests passed! The audit system foundation is working.")
        sys.exit(0)
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please check the error messages above.")
        sys.exit(1)
