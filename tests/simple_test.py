#!/usr/bin/env python3
"""
Simple Jarvis AI API Test Script

This script runs basic API tests without complex dependencies.
"""

import json
import time
import requests
import statistics
from typing import Dict, List, Any


def test_endpoints(base_url="http://127.0.0.1:8000"):
    """Test all Jarvis AI API endpoints."""
    
    print("🚀 Starting Simple Jarvis AI API Testing")
    print("=" * 60)
    
    test_results = []
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        test_results.append({
            "test": "Health Check",
            "endpoint": "/health",
            "method": "GET",
            "status_code": response.status_code,
            "success": response.status_code == 200,
            "response_time_ms": response.elapsed.total_seconds() * 1000
        })
        print(f"✅ Health Check: {response.status_code}")
    except Exception as e:
        test_results.append({
            "test": "Health Check",
            "endpoint": "/health",
            "method": "GET",
            "status_code": None,
            "success": False,
            "error": str(e)
        })
        print(f"❌ Health Check: {e}")
    
    # Test core API endpoints
    core_endpoints = [
        ("/api/v1/models", "GET", "List Models"),
        ("/api/v1/personas", "GET", "List Personas"),
        ("/api/v1/chat", "POST", "Chat Completion", {"messages": [{"role": "user", "content": "Hello"}], "persona": "generalist"}),
        ("/api/v1/monitoring/metrics", "GET", "Get Metrics"),
        ("/api/v1/monitoring/traces", "GET", "Get Traces"),
        ("/api/v1/management/system/status", "GET", "System Status"),
        ("/api/v1/management/routing/config", "GET", "Routing Config"),
        ("/api/v1/management/backends", "GET", "List Backends"),
        ("/api/v1/management/context/config", "GET", "Context Config"),
        ("/api/v1/management/security/status", "GET", "Security Status"),
        ("/v1/chat/completions", "POST", "OpenAI Chat", {"model": "test", "messages": [{"role": "user", "content": "Hello"}]}),
        ("/v1/models", "GET", "OpenAI Models")
    ]
    
    for endpoint, method, test_name, *data in core_endpoints:
        try:
            url = f"{base_url}{endpoint}"
            json_data = data[0] if data else None
            
            if method == "GET":
                response = requests.get(url, timeout=10)
            else:
                response = requests.post(url, json=json_data, timeout=10)
            
            test_results.append({
                "test": test_name,
                "endpoint": endpoint,
                "method": method,
                "status_code": response.status_code,
                "success": response.status_code in [200, 201],
                "response_time_ms": response.elapsed.total_seconds() * 1000
            })
            print(f"✅ {test_name}: {response.status_code}")
            
        except Exception as e:
            test_results.append({
                "test": test_name,
                "endpoint": endpoint,
                "method": method,
                "status_code": None,
                "success": False,
                "error": str(e)
            })
            print(f"❌ {test_name}: {e}")
    
    # Test error handling
    error_tests = [
        ("/nonexistent", "GET", "404 Not Found"),
        ("/api/v1/chat", "POST", "Invalid JSON", {"invalid": "data"}),
    ]
    
    for endpoint, method, test_name, *data in error_tests:
        try:
            url = f"{base_url}{endpoint}"
            json_data = data[0] if data else None
            
            if method == "GET":
                response = requests.get(url, timeout=10)
            else:
                response = requests.post(url, json=json_data, timeout=10)
            
            expected_status = 404 if "404" in test_name else 422
            test_results.append({
                "test": test_name,
                "endpoint": endpoint,
                "method": method,
                "status_code": response.status_code,
                "success": response.status_code == expected_status,
                "response_time_ms": response.elapsed.total_seconds() * 1000
            })
            print(f"✅ {test_name}: {response.status_code}")
            
        except Exception as e:
            test_results.append({
                "test": test_name,
                "endpoint": endpoint,
                "method": method,
                "status_code": None,
                "success": False,
                "error": str(e)
            })
            print(f"❌ {test_name}: {e}")
    
    # Generate summary
    total_tests = len(test_results)
    successful_tests = len([r for r in test_results if r["success"]])
    failed_tests = total_tests - successful_tests
    response_times = [r["response_time_ms"] for r in test_results if r["success"]]
    
    summary = {
        "total_tests": total_tests,
        "successful_tests": successful_tests,
        "failed_tests": failed_tests,
        "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
        "avg_response_time_ms": statistics.mean(response_times) if response_times else 0,
        "min_response_time_ms": min(response_times) if response_times else 0,
        "max_response_time_ms": max(response_times) if response_times else 0
    }
    
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Successful: {summary['successful_tests']}")
    print(f"Failed: {summary['failed_tests']}")
    print(f"Success Rate: {summary['success_rate']:.1%}")
    print(f"Average Response Time: {summary['avg_response_time_ms']:.2f}ms")
    
    # Save detailed results
    report = {
        "summary": summary,
        "test_results": test_results,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "server_url": base_url
    }
    
    with open("simple_test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("📊 Detailed report saved to simple_test_report.json")
    
    return report


if __name__ == "__main__":
    test_endpoints()
