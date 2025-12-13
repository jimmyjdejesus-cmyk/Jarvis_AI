#!/usr/bin/env python3
"""
Contract Testing Runner

This script runs all contract tests and generates comprehensive reports.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.contract_tests.test_api_contracts import run_contract_tests
from tests.contract_tests.test_performance_contracts import run_performance_tests
from tests.contract_tests.test_integration_contracts import run_integration_tests


async def run_all_contract_tests():
    """Run all contract test suites and generate unified report."""
    print("🚀 Starting Comprehensive Contract Testing Suite")
    print("=" * 80)
    
    test_results = {
        'api_contracts': {'status': 'pending', 'details': {}},
        'performance_contracts': {'status': 'pending', 'details': {}},
        'integration_contracts': {'status': 'pending', 'details': {}}
    }
    
    try:
        # Run API Contract Tests
        print("\n📋 PHASE 1: API Contract Testing")
        print("-" * 40)
        try:
            await run_contract_tests()
            test_results['api_contracts']['status'] = 'passed'
            print("✅ API Contract Tests: PASSED")
        except Exception as e:
            test_results['api_contracts']['status'] = 'failed'
            test_results['api_contracts']['details']['error'] = str(e)
            print(f"❌ API Contract Tests: FAILED - {e}")
        
        # Run Performance Contract Tests
        print("\n⚡ PHASE 2: Performance Contract Testing")
        print("-" * 40)
        try:
            await run_performance_tests()
            test_results['performance_contracts']['status'] = 'passed'
            print("✅ Performance Contract Tests: PASSED")
        except Exception as e:
            test_results['performance_contracts']['status'] = 'failed'
            test_results['performance_contracts']['details']['error'] = str(e)
            print(f"❌ Performance Contract Tests: FAILED - {e}")
        
        # Run Integration Contract Tests
        print("\n🔄 PHASE 3: Integration Contract Testing")
        print("-" * 40)
        try:
            await run_integration_tests()
            test_results['integration_contracts']['status'] = 'passed'
            print("✅ Integration Contract Tests: PASSED")
        except Exception as e:
            test_results['integration_contracts']['status'] = 'failed'
            test_results['integration_contracts']['details']['error'] = str(e)
            print(f"❌ Integration Contract Tests: FAILED - {e}")
        
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {e}")
        sys.exit(1)
    
    # Generate final summary
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE CONTRACT TEST SUMMARY")
    print("=" * 80)
    
    passed_tests = sum(1 for result in test_results.values() if result['status'] == 'passed')
    total_tests = len(test_results)
    overall_success_rate = passed_tests / total_tests
    
    for test_type, result in test_results.items():
        status_emoji = "✅" if result['status'] == 'passed' else "❌"
        status_text = "PASSED" if result['status'] == 'passed' else "FAILED"
        print(f"{status_emoji} {test_type.replace('_', ' ').title()}: {status_text}")
        
        if result['status'] == 'failed' and 'error' in result['details']:
            print(f"   └─ Error: {result['details']['error']}")
    
    print(f"\n📈 Overall Success Rate: {overall_success_rate:.1%} ({passed_tests}/{total_tests})")
    
    # Save test results
    results_file = project_root / "contract_test_results.json"
    import json
    from datetime import datetime
    
    final_report = {
        'timestamp': datetime.now().isoformat(),
        'overall_success_rate': overall_success_rate,
        'passed_tests': passed_tests,
        'total_tests': total_tests,
        'test_results': test_results
    }
    
    with open(results_file, 'w') as f:
        json.dump(final_report, f, indent=2)
    
    print(f"📄 Detailed results saved to: {results_file}")
    
    # Exit with appropriate code
    if overall_success_rate < 1.0:
        failed_count = total_tests - passed_tests
        print(f"\n❌ {failed_count} test suite(s) failed. Contract testing incomplete.")
        sys.exit(1)
    else:
        print("\n🎉 All contract tests passed! API contracts are fully validated.")
        sys.exit(0)


def main():
    """Main entry point."""
    try:
        asyncio.run(run_all_contract_tests())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
