"""
Performance Contract Testing Suite

This module implements performance-based contract testing for API endpoints,
validating response times, throughput, and performance regression detection.
"""

import pytest
import asyncio
import time
import statistics
from typing import Dict, Any, List
from pathlib import Path
import httpx
import json
import yaml
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class PerformanceThresholds:
    """Performance thresholds for different endpoint types."""
    max_response_time_ms: int
    min_throughput_rps: float
    max_p95_response_time_ms: int
    max_p99_response_time_ms: int


@dataclass
class PerformanceResult:
    """Performance test result."""
    endpoint: str
    method: str
    response_time_ms: float
    status_code: int
    timestamp: datetime
    passed: bool
    violations: List[str]


class PerformanceContractTester:
    """Performance contract testing and validation."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000", api_key: str = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=60.0)
        self.performance_results = []
        
        # Define performance thresholds for different endpoint types
        self.thresholds = {
            '/health': PerformanceThresholds(100, 100.0, 150, 200),
            '/models': PerformanceThresholds(200, 50.0, 300, 500),
            '/chat': PerformanceThresholds(5000, 10.0, 8000, 12000),
            '/agents': PerformanceThresholds(1000, 20.0, 1500, 2500),
            '/monitoring/metrics': PerformanceThresholds(500, 30.0, 800, 1200),
            '/jobs': PerformanceThresholds(300, 40.0, 500, 800),
        }
    
    async def measure_endpoint_performance(
        self, 
        endpoint: str, 
        method: str, 
        payload: Dict[str, Any] = None,
        headers: Dict[str, Any] = None
    ) -> PerformanceResult:
        """Measure single endpoint performance."""
        start_time = time.time()
        violations = []
        
        try:
            request_headers = headers or {}
            if self.api_key:
                request_headers['X-API-Key'] = self.api_key
                
            # Make request
            response = await self.client.request(
                method=method,
                url=f"{self.base_url}{endpoint}",
                json=payload,
                headers=request_headers
            )
            
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            
            # Check performance thresholds
            threshold = self._get_threshold_for_endpoint(endpoint)
            if threshold:
                if response_time_ms > threshold.max_response_time_ms:
                    violations.append(f"Response time {response_time_ms:.2f}ms exceeds max threshold {threshold.max_response_time_ms}ms")
                    
            result = PerformanceResult(
                endpoint=endpoint,
                method=method,
                response_time_ms=response_time_ms,
                status_code=response.status_code,
                timestamp=datetime.now(),
                passed=len(violations) == 0,
                violations=violations
            )
            
            return result
            
        except Exception as e:
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            
            return PerformanceResult(
                endpoint=endpoint,
                method=method,
                response_time_ms=response_time_ms,
                status_code=0,
                timestamp=datetime.now(),
                passed=False,
                violations=[f"Request failed: {str(e)}"]
            )
    
    def _get_threshold_for_endpoint(self, endpoint: str):
        """Get performance threshold for endpoint."""
        for path, threshold in self.thresholds.items():
            if endpoint.startswith(path):
                return threshold
        return None
    
    async def test_endpoint_performance(
        self, 
        endpoint: str, 
        method: str, 
        iterations: int = 10,
        payload: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Test endpoint performance across multiple iterations."""
        print(f"🧪 Testing performance for {method} {endpoint} ({iterations} iterations)")
        
        results = []
        for i in range(iterations):
            result = await self.measure_endpoint_performance(endpoint, method, payload)
            results.append(result)
            self.performance_results.append(result)
            
            # Small delay between requests
            if i < iterations - 1:
                await asyncio.sleep(0.1)
        
        # Calculate statistics
        response_times = [r.response_time_ms for r in results]
        success_rate = sum(1 for r in results if r.status_code < 400) / len(results)
        
        stats = {
            'endpoint': endpoint,
            'method': method,
            'iterations': iterations,
            'success_rate': success_rate,
            'response_times': {
                'mean': statistics.mean(response_times),
                'median': statistics.median(response_times),
                'min': min(response_times),
                'max': max(response_times),
                'p95': self._percentile(response_times, 95),
                'p99': self._percentile(response_times, 99),
            },
            'violations': sum(len(r.violations) for r in results),
            'all_passed': all(r.passed for r in results)
        }
        
        # Check threshold violations
        threshold = self._get_threshold_for_endpoint(endpoint)
        if threshold:
            if stats['response_times']['mean'] > threshold.max_response_time_ms:
                stats['threshold_violation'] = f"Mean response time {stats['response_times']['mean']:.2f}ms exceeds {threshold.max_response_time_ms}ms"
            if stats['response_times']['p95'] > threshold.max_p95_response_time_ms:
                stats['p95_violation'] = f"P95 response time {stats['response_times']['p95']:.2f}ms exceeds {threshold.max_p95_response_time_ms}ms"
        
        return stats
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile from data."""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    async def test_load_performance(self, endpoint: str, method: str, concurrent_requests: int = 5, duration_seconds: int = 10):
        """Test endpoint under concurrent load."""
        print(f"🚛 Testing load performance for {method} {endpoint} ({concurrent_requests} concurrent, {duration_seconds}s duration)")
        
        start_time = time.time()
        tasks = []
        results = []
        
        async def make_request():
            while time.time() - start_time < duration_seconds:
                result = await self.measure_endpoint_performance(endpoint, method)
                results.append(result)
                await asyncio.sleep(0.1)  # Brief pause between requests
        
        # Create concurrent tasks
        for _ in range(concurrent_requests):
            task = asyncio.create_task(make_request())
            tasks.append(task)
        
        # Wait for all tasks to complete
        await asyncio.gather(*tasks)
        
        # Calculate load test statistics
        successful_requests = [r for r in results if r.status_code < 400]
        throughput = len(successful_requests) / duration_seconds
        
        response_times = [r.response_time_ms for r in successful_requests]
        
        load_stats = {
            'endpoint': endpoint,
            'method': method,
            'concurrent_requests': concurrent_requests,
            'duration_seconds': duration_seconds,
            'total_requests': len(results),
            'successful_requests': len(successful_requests),
            'failed_requests': len(results) - len(successful_requests),
            'throughput_rps': throughput,
            'response_times': {
                'mean': statistics.mean(response_times) if response_times else 0,
                'median': statistics.median(response_times) if response_times else 0,
                'p95': self._percentile(response_times, 95) if response_times else 0,
                'p99': self._percentile(response_times, 99) if response_times else 0,
            }
        }
        
        return load_stats
    
    async def test_performance_regression(self, baseline_file: str = "performance_baseline.json"):
        """Test for performance regression against baseline."""
        baseline_path = Path(__file__).parent / baseline_file
        
        if not baseline_path.exists():
            print(f"⚠️ No baseline file found at {baseline_path}")
            return {'regression_detected': False, 'message': 'No baseline for comparison'}
        
        try:
            with open(baseline_path, 'r') as f:
                baseline = json.load(f)
        except Exception as e:
            print(f"❌ Error loading baseline: {e}")
            return {'regression_detected': False, 'message': f'Error loading baseline: {e}'}
        
        regression_results = []
        
        for endpoint, baseline_stats in baseline.items():
            # Run current performance test
            current_stats = await self.test_endpoint_performance(
                endpoint['path'], 
                endpoint['method'], 
                iterations=5
            )
            
            # Compare with baseline
            regression_detected = False
            violations = []
            
            # Check response time regression
            if 'response_time_ms' in baseline_stats and 'mean' in current_stats['response_times']:
                baseline_mean = baseline_stats['response_time_ms']['mean']
                current_mean = current_stats['response_times']['mean']
                
                # Consider regression if current performance is 20% worse than baseline
                if current_mean > baseline_mean * 1.2:
                    regression_detected = True
                    violations.append(f"Response time regression: {current_mean:.2f}ms vs baseline {baseline_mean:.2f}ms")
            
            regression_results.append({
                'endpoint': endpoint,
                'baseline': baseline_stats,
                'current': current_stats,
                'regression_detected': regression_detected,
                'violations': violations
            })
        
        return {
            'regression_detected': any(r['regression_detected'] for r in regression_results),
            'results': regression_results
        }
    
    async def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        if not self.performance_results:
            return {'error': 'No performance data available'}
        
        # Group results by endpoint
        results_by_endpoint = {}
        for result in self.performance_results:
            key = f"{result.method} {result.endpoint}"
            if key not in results_by_endpoint:
                results_by_endpoint[key] = []
            results_by_endpoint[key].append(result)
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_requests': len(self.performance_results),
                'total_endpoints': len(results_by_endpoint),
                'overall_success_rate': sum(1 for r in self.performance_results if r.passed) / len(self.performance_results)
            },
            'endpoints': {}
        }
        
        for endpoint_key, results in results_by_endpoint.items():
            response_times = [r.response_time_ms for r in results]
            success_rate = sum(1 for r in results if r.passed) / len(results)
            
            report['endpoints'][endpoint_key] = {
                'total_requests': len(results),
                'success_rate': success_rate,
                'response_times': {
                    'mean': statistics.mean(response_times),
                    'median': statistics.median(response_times),
                    'min': min(response_times),
                    'max': max(response_times),
                    'p95': self._percentile(response_times, 95),
                    'p99': self._percentile(response_times, 99),
                },
                'violations': sum(len(r.violations) for r in results)
            }
        
        return report
    
    async def save_performance_baseline(self, filename: str = "performance_baseline.json"):
        """Save current performance as baseline for regression testing."""
        report = await self.generate_performance_report()
        
        baseline_data = {}
        for endpoint, stats in report.get('endpoints', {}).items():
            baseline_data[endpoint] = {
                'response_time_ms': stats['response_times'],
                'success_rate': stats['success_rate'],
                'timestamp': datetime.now().isoformat()
            }
        
        baseline_path = Path(__file__).parent / filename
        with open(baseline_path, 'w') as f:
            json.dump(baseline_data, f, indent=2)
        
        print(f"✅ Performance baseline saved to {baseline_path}")
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


class PerformanceContractTestSuite:
    """Performance contract test suite."""
    
    @pytest.fixture
    def perf_tester(self):
        return PerformanceContractTester()
    
    async def test_all_endpoints_performance(self, perf_tester: PerformanceContractTester):
        """Test performance for all API endpoints."""
        test_endpoints = [
            {'endpoint': '/health', 'method': 'GET'},
            {'endpoint': '/models', 'method': 'GET'},
            {'endpoint': '/agents', 'method': 'GET'},
            {'endpoint': '/monitoring/metrics', 'method': 'GET'},
            {'endpoint': '/chat', 'method': 'POST', 'payload': {'messages': [{'role': 'user', 'content': 'Hello'}]}},
        ]
        
        results = []
        
        for test_case in test_endpoints:
            try:
                stats = await perf_tester.test_endpoint_performance(
                    endpoint=test_case['endpoint'],
                    method=test_case['method'],
                    payload=test_case.get('payload'),
                    iterations=5
                )
                results.append(stats)
                
                # Assert performance requirements
                assert stats['all_passed'], f"Performance test failed for {test_case['endpoint']}"
                assert stats['success_rate'] >= 0.95, f"Success rate below 95% for {test_case['endpoint']}"
                
                print(f"✅ Performance test passed for {test_case['endpoint']}")
                
            except Exception as e:
                print(f"❌ Performance test failed for {test_case['endpoint']}: {e}")
                raise
        
        return results
    
    async def test_load_performance(self, perf_tester: PerformanceContractTester):
        """Test endpoints under load."""
        load_test_cases = [
            {'endpoint': '/health', 'method': 'GET', 'concurrent': 10, 'duration': 5},
            {'endpoint': '/models', 'method': 'GET', 'concurrent': 5, 'duration': 5},
        ]
        
        results = []
        
        for test_case in load_test_cases:
            try:
                stats = await perf_tester.test_load_performance(
                    endpoint=test_case['endpoint'],
                    method=test_case['method'],
                    concurrent_requests=test_case['concurrent'],
                    duration_seconds=test_case['duration']
                )
                results.append(stats)
                
                # Assert load test requirements
                assert stats['throughput_rps'] > 1.0, f"Throughput below 1 RPS for {test_case['endpoint']}"
                assert stats['failed_requests'] == 0, f"Failed requests in load test for {test_case['endpoint']}"
                
                print(f"✅ Load test passed for {test_case['endpoint']}")
                
            except Exception as e:
                print(f"❌ Load test failed for {test_case['endpoint']}: {e}")
                raise
        
        return results


# Test execution functions
async def run_performance_tests():
    """Run all performance tests."""
    tester = PerformanceContractTester()
    
    print("🚀 Starting Performance Contract Testing")
    print("=" * 60)
    
    try:
        # Test individual endpoint performance
        await tester.test_all_endpoints_performance()
        
        # Test load performance
        await tester.test_load_performance()
        
        # Generate and save baseline
        await tester.save_performance_baseline()
        
        # Generate report
        report = await tester.generate_performance_report()
        
        print("\n📊 Performance Test Summary:")
        print(f"Total requests: {report['summary']['total_requests']}")
        print(f"Overall success rate: {report['summary']['overall_success_rate']:.2%}")
        
        print("\n✅ All performance tests completed!")
        
    except Exception as e:
        print(f"\n❌ Performance tests failed: {e}")
        raise
    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(run_performance_tests())
