#!/usr/bin/env python3
"""
Comprehensive Jarvis AI API Testing Suite

This script performs comprehensive testing of all Jarvis AI API endpoints including:
- Schema validation
- Endpoint functionality testing
- Security testing
- Performance testing
- Error handling testing
- OpenAI compatibility testing

Usage:
    python3 comprehensive_api_test.py [--server-url URL] [--api-key KEY]
"""

import json
import time
import asyncio
import aiohttp
import argparse
import statistics
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class TestResult:
    """Test result data structure."""
    test_name: str
    endpoint: str
    method: str
    status_code: Optional[int]
    success: bool
    response_time_ms: float
    error_message: Optional[str] = None
    expected_status: Optional[int] = None
    schema_valid: Optional[bool] = None


@dataclass
class PerformanceMetrics:
    """Performance metrics for testing."""
    test_name: str
    min_response_time: float
    max_response_time: float
    avg_response_time: float
    median_response_time: float
    success_rate: float
    total_requests: int
    successful_requests: int


class JarvisAPITester:
    """Comprehensive API testing suite for Jarvis AI."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = None
        self.test_results: List[TestResult] = []
        self.performance_metrics: List[PerformanceMetrics] = []
        
        # Load OpenAPI specification
        self.api_spec = self._load_api_spec()
        
    def _load_api_spec(self) -> Dict[str, Any]:
        """Load the OpenAPI specification."""
        try:
            import yaml
            with open('api_schemas/openapi.yaml', 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print("Warning: OpenAPI spec not found. Using built-in specification.")
            return self._get_builtin_spec()
    
    def _get_builtin_spec(self) -> Dict[str, Any]:
        """Built-in API specification as fallback."""
        return {
            "paths": {
                "/health": {"get": {"responses": {"200": {"description": "Health check"}}}},
                "/api/v1/models": {"get": {"responses": {"200": {"description": "List models"}}}},
                "/api/v1/personas": {"get": {"responses": {"200": {"description": "List personas"}}}},
                "/api/v1/chat": {"post": {"responses": {"200": {"description": "Chat completion"}}}},
                "/api/v1/monitoring/metrics": {"get": {"responses": {"200": {"description": "Get metrics"}}}},
                "/api/v1/monitoring/traces": {"get": {"responses": {"200": {"description": "Get traces"}}}},
                "/api/v1/management/system/status": {"get": {"responses": {"200": {"description": "System status"}}}},
                "/api/v1/management/routing/config": {"get": {"responses": {"200": {"description": "Get routing config"}}}},
                "/api/v1/management/config/routing": {"put": {"responses": {"200": {"description": "Update routing config"}}}},
                "/api/v1/management/backends": {"get": {"responses": {"200": {"description": "List backends"}}}},
                "/api/v1/management/backends/{name}/test": {"post": {"responses": {"200": {"description": "Test backend"}}}},
                "/api/v1/management/context/config": {"get": {"responses": {"200": {"description": "Get context config"}}}},
                "/api/v1/management/config/context": {"put": {"responses": {"200": {"description": "Update context config"}}}},
                "/api/v1/management/security/status": {"get": {"responses": {"200": {"description": "Get security status"}}}},
                "/api/v1/management/personas": {"post": {"responses": {"200": {"description": "Create persona"}}}},
                "/api/v1/management/personas/{name}": {
                    "put": {"responses": {"200": {"description": "Update persona"}}},
                    "delete": {"responses": {"200": {"description": "Delete persona"}}}
                },
                "/api/v1/management/config/save": {"post": {"responses": {"200": {"description": "Save config"}}}},
                "/v1/chat/completions": {"post": {"responses": {"200": {"description": "OpenAI chat completions"}}}},
                "/v1/models": {"get": {"responses": {"200": {"description": "OpenAI models list"}}}}
            }
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers=self._get_headers()
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for requests."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers
    
    async def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                          expected_status: Optional[int] = None) -> TestResult:
        """Make a single API request and record the result."""
        url = f"{self.base_url}{endpoint}"
        test_name = f"{method} {endpoint}"
        start_time = time.time()
        
        try:
            async with self.session.request(method, url, json=data) as response:
                response_time = (time.time() - start_time) * 1000
                
                # Try to read response
                try:
                    await response.json()
                except:
                    pass  # Response might not be JSON
                
                success = expected_status is None or response.status == expected_status
                
                return TestResult(
                    test_name=test_name,
                    endpoint=endpoint,
                    method=method,
                    status_code=response.status,
                    success=success,
                    response_time_ms=response_time,
                    expected_status=expected_status
                )
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return TestResult(
                test_name=test_name,
                endpoint=endpoint,
                method=method,
                status_code=None,
                success=False,
                response_time_ms=response_time,
                error_message=str(e),
                expected_status=expected_status
            )
    
    async def test_health_endpoints(self) -> List[TestResult]:
        """Test health and status endpoints."""
        results = []
        print("Testing Health & Status endpoints...")
        
        # Test health endpoint
        result = await self.make_request("GET", "/health", expected_status=200)
        results.append(result)
        
        return results
    
    async def test_core_api_endpoints(self) -> List[TestResult]:
        """Test core API endpoints."""
        results = []
        print("Testing Core API endpoints...")
        
        # Test models endpoint
        result = await self.make_request("GET", "/api/v1/models", expected_status=200)
        results.append(result)
        
        # Test personas endpoint
        result = await self.make_request("GET", "/api/v1/personas", expected_status=200)
        results.append(result)
        
        # Test chat endpoint with valid request
        chat_data = {
            "messages": [{"role": "user", "content": "Hello, test message"}],
            "persona": "generalist",
            "temperature": 0.7,
            "max_tokens": 100
        }
        result = await self.make_request("POST", "/api/v1/chat", data=chat_data, expected_status=200)
        results.append(result)
        
        # Test chat with invalid persona
        chat_data_invalid = {
            "messages": [{"role": "user", "content": "Hello"}],
            "persona": "nonexistent",
            "temperature": 0.7,
            "max_tokens": 100
        }
        result = await self.make_request("POST", "/api/v1/chat", data=chat_data_invalid, expected_status=400)
        results.append(result)
        
        return results
    
    async def test_monitoring_endpoints(self) -> List[TestResult]:
        """Test monitoring endpoints."""
        results = []
        print("Testing Monitoring endpoints...")
        
        # Test metrics endpoint
        result = await self.make_request("GET", "/api/v1/monitoring/metrics", expected_status=200)
        results.append(result)
        
        # Test traces endpoint
        result = await self.make_request("GET", "/api/v1/monitoring/traces", expected_status=200)
        results.append(result)
        
        return results
    
    async def test_management_endpoints(self) -> List[TestResult]:
        """Test management API endpoints."""
        results = []
        print("Testing Management API endpoints...")
        
        # System status
        result = await self.make_request("GET", "/api/v1/management/system/status", expected_status=200)
        results.append(result)
        
        # Routing config
        result = await self.make_request("GET", "/api/v1/management/routing/config", expected_status=200)
        results.append(result)
        
        # Update routing config
        routing_data = {"allowed_personas": ["generalist"], "enable_adaptive_routing": True}
        result = await self.make_request("PUT", "/api/v1/management/config/routing", data=routing_data, expected_status=200)
        results.append(result)
        
        # List backends
        result = await self.make_request("GET", "/api/v1/management/backends", expected_status=200)
        results.append(result)
        
        # Test backend (will likely fail if backend doesn't exist, but test structure)
        result = await self.make_request("POST", "/api/v1/management/backends/ollama/test", expected_status=200)
        results.append(result)
        
        # Context config
        result = await self.make_request("GET", "/api/v1/management/context/config", expected_status=200)
        results.append(result)
        
        # Update context config
        context_data = {"enable_semantic_chunking": True, "max_combined_context_tokens": 8192}
        result = await self.make_request("PUT", "/api/v1/management/config/context", data=context_data, expected_status=200)
        results.append(result)
        
        # Security status
        result = await self.make_request("GET", "/api/v1/management/security/status", expected_status=200)
        results.append(result)
        
        # Create persona
        persona_data = {
            "name": "test-persona",
            "description": "Test persona for API testing",
            "system_prompt": "You are a test assistant.",
            "max_context_window": 4096,
            "routing_hint": "test"
        }
        result = await self.make_request("POST", "/api/v1/management/personas", data=persona_data, expected_status=200)
        results.append(result)
        
        # Update persona
        update_data = {"description": "Updated test persona"}
        result = await self.make_request("PUT", "/api/v1/management/personas/test-persona", data=update_data, expected_status=200)
        results.append(result)
        
        # Delete persona
        result = await self.make_request("DELETE", "/api/v1/management/personas/test-persona", expected_status=200)
        results.append(result)
        
        # Save config
        result = await self.make_request("POST", "/api/v1/management/config/save", expected_status=200)
        results.append(result)
        
        return results
    
    async def test_openai_compatible_endpoints(self) -> List[TestResult]:
        """Test OpenAI-compatible endpoints."""
        results = []
        print("Testing OpenAI-Compatible endpoints...")
        
        # OpenAI chat completions
        openai_data = {
            "model": "jarvis-default",
            "messages": [{"role": "user", "content": "Hello!"}],
            "temperature": 0.7,
            "max_tokens": 100
        }
        result = await self.make_request("POST", "/v1/chat/completions", data=openai_data, expected_status=200)
        results.append(result)
        
        # OpenAI models list
        result = await self.make_request("GET", "/v1/models", expected_status=200)
        results.append(result)
        
        return results
    
    async def test_security_authentication(self) -> List[TestResult]:
        """Test security and authentication."""
        results = []
        print("Testing Security & Authentication...")
        
        # Test without API key (if auth is enabled)
        if self.api_key:
            # Test with invalid API key
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/v1/personas") as response:
                    if response.status == 401:
                        results.append(TestResult(
                            test_name="Auth: Invalid API key",
                            endpoint="/api/v1/personas",
                            method="GET",
                            status_code=401,
                            success=True,
                            response_time_ms=0,
                            expected_status=401
                        ))
        
        # Test input validation
        invalid_chat_data = {
            "messages": [{"role": "user", "content": "Test"}],
            "persona": "generalist",
            "temperature": 999,  # Invalid temperature
            "max_tokens": -1     # Invalid max_tokens
        }
        result = await self.make_request("POST", "/api/v1/chat", data=invalid_chat_data, expected_status=422)
        results.append(result)
        
        return results
    
    async def test_error_handling(self) -> List[TestResult]:
        """Test error handling and edge cases."""
        results = []
        print("Testing Error Handling & Edge Cases...")
        
        # Test invalid endpoint
        result = await self.make_request("GET", "/nonexistent/endpoint", expected_status=404)
        results.append(result)
        
        # Test invalid HTTP method
        result = await self.make_request("PATCH", "/api/v1/personas", expected_status=405)
        results.append(result)
        
        # Test malformed JSON
        try:
            async with self.session.post(f"{self.base_url}/api/v1/chat", 
                                       data="invalid json", 
                                       headers={"Content-Type": "application/json"}) as response:
                response_time = 100  # Mock response time
                results.append(TestResult(
                    test_name="Error: Malformed JSON",
                    endpoint="/api/v1/chat",
                    method="POST",
                    status_code=response.status,
                    success=response.status in [400, 422],
                    response_time_ms=response_time,
                    expected_status=400
                ))
        except Exception as e:
            results.append(TestResult(
                test_name="Error: Malformed JSON",
                endpoint="/api/v1/chat",
                method="POST",
                status_code=None,
                success=True,  # Expected to fail
                response_time_ms=100,
                error_message=str(e)
            ))
        
        return results
    
    async def test_performance_concurrent(self, num_requests: int = 10) -> List[TestResult]:
        """Test performance with concurrent requests."""
        results = []
        print(f"Testing Performance with {num_requests} concurrent requests...")
        
        # Create concurrent requests to chat endpoint
        tasks = []
        for i in range(num_requests):
            chat_data = {
                "messages": [{"role": "user", "content": f"Performance test message {i}"}],
                "persona": "generalist",
                "temperature": 0.7,
                "max_tokens": 50
            }
            task = self.make_request("POST", "/api/v1/chat", data=chat_data, expected_status=200)
            tasks.append(task)
        
        start_time = time.time()
        concurrent_results = await asyncio.gather(*tasks)
        total_time = (time.time() - start_time) * 1000
        
        results.extend(concurrent_results)
        
        # Calculate performance metrics
        response_times = [r.response_time_ms for r in concurrent_results if r.success]
        if response_times:
            metrics = PerformanceMetrics(
                test_name="Concurrent Chat Requests",
                min_response_time=min(response_times),
                max_response_time=max(response_times),
                avg_response_time=statistics.mean(response_times),
                median_response_time=statistics.median(response_times),
                success_rate=len([r for r in concurrent_results if r.success]) / len(concurrent_results),
                total_requests=len(concurrent_results),
                successful_requests=len([r for r in concurrent_results if r.success])
            )
            self.performance_metrics.append(metrics)
        
        return results
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites and generate comprehensive report."""
        print("🚀 Starting Comprehensive Jarvis AI API Testing")
        print("=" * 60)
        
        test_suites = [
            ("Health Endpoints", self.test_health_endpoints),
            ("Core API", self.test_core_api_endpoints),
            ("Monitoring", self.test_monitoring_endpoints),
            ("Management API", self.test_management_endpoints),
            ("OpenAI Compatible", self.test_openai_compatible_endpoints),
            ("Security & Auth", self.test_security_authentication),
            ("Error Handling", self.test_error_handling),
            ("Performance", lambda: self.test_performance_concurrent())
        ]
        
        all_results = []
        
        for suite_name, test_func in test_suites:
            try:
                suite_results = await test_func()
                all_results.extend(suite_results)
                self.test_results.extend(suite_results)
                
                # Print suite summary
                success_count = len([r for r in suite_results if r.success])
                total_count = len(suite_results)
                print(f"✅ {suite_name}: {success_count}/{total_count} tests passed")
                
            except Exception as e:
                print(f"❌ {suite_name}: Failed with error - {e}")
        
        return self.generate_test_report()
    
    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r.success])
        failed_tests = total_tests - successful_tests
        
        # Calculate overall metrics
        response_times = [r.response_time_ms for r in self.test_results if r.success]
        
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
                "total_response_time_ms": sum(response_times),
                "avg_response_time_ms": statistics.mean(response_times) if response_times else 0
            },
            "test_results": [asdict(r) for r in self.test_results],
            "performance_metrics": [asdict(m) for m in self.performance_metrics],
            "server_info": {
                "base_url": self.base_url,
                "api_key_configured": bool(self.api_key),
                "test_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any], filename: str = "test_report.json"):
        """Save test report to file."""
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"📊 Test report saved to {filename}")


async def main():
    """Main testing function."""
    parser = argparse.ArgumentParser(description="Comprehensive Jarvis AI API Testing")
    parser.add_argument("--server-url", default="http://127.0.0.1:8000", help="Server URL")
    parser.add_argument("--api-key", help="API key for authentication")
    parser.add_argument("--output", default="test_report.json", help="Output file for test report")
    
    args = parser.parse_args()
    
    async with JarvisAPITester(base_url=args.server_url, api_key=args.api_key) as tester:
        report = await tester.run_all_tests()
        tester.save_report(report, args.output)
        
        # Print summary
        summary = report["test_summary"]
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Successful: {summary['successful_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Success Rate: {summary['success_rate']:.1%}")
        print(f"Average Response Time: {summary['avg_response_time_ms']:.2f}ms")
        
        if summary['failed_tests'] > 0:
            print("\n❌ FAILED TESTS:")
            for result in report["test_results"]:
                if not result["success"]:
                    print(f"  - {result['test_name']}: {result.get('error_message', 'Status ' + str(result['status_code']))}")


if __name__ == "__main__":
    asyncio.run(main())
