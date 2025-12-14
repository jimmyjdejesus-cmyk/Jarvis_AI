"""Comprehensive integration test for unified Jarvis AI system."""

import asyncio
import json
import requests
import time
import sys
from pathlib import Path
from typing import Dict, Any, List

class IntegrationTester:
    """Test suite for validating all integrations."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.results = []
        self.failed_tests = []
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result."""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": time.time()
        }
        self.results.append(result)
        
        if not success:
            self.failed_tests.append(test_name)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
    
    def test_health_endpoint(self) -> bool:
        """Test basic health endpoint."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Endpoint", True, f"Status: {data.get('status')}")
                return True
            else:
                self.log_test("Health Endpoint", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Endpoint", False, str(e))
            return False
    
    def test_models_endpoint(self) -> bool:
        """Test models endpoint."""
        try:
            response = requests.get(f"{self.base_url}/api/models", timeout=20)
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                self.log_test("Models Endpoint", True, f"Found {len(models)} models")
                return True
            else:
                self.log_test("Models Endpoint", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Models Endpoint", False, str(e))
            return False
    
    def test_agents_endpoint(self) -> bool:
        """Test agents endpoint."""
        try:
            response = requests.get(f"{self.base_url}/api/agents", timeout=10)
            if response.status_code == 200:
                data = response.json()
                agents = data.get("agents", [])
                self.log_test("Agents Endpoint", True, f"Found {len(agents)} agents")
                return True
            else:
                self.log_test("Agents Endpoint", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Agents Endpoint", False, str(e))
            return False
    
    def test_chat_endpoint(self) -> bool:
        """Test chat endpoint."""
        try:
            payload = {
                "messages": [
                    {"role": "user", "content": "Hello, this is a test message."}
                ]
            }
            response = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=60)
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", "")
                self.log_test("Chat Endpoint", True, f"Response length: {len(content)} chars")
                return True
            else:
                self.log_test("Chat Endpoint", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Chat Endpoint", False, str(e))
            return False
    
    def test_agent_execution(self) -> bool:
        """Test agent execution endpoint."""
        try:
            payload = {
                "agent_type": "research",
                "objective": "Test research task",
                "context": {"test": True}
            }
            response = requests.post(f"{self.base_url}/api/agents/execute", json=payload, timeout=60)
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                self.log_test("Agent Execution", success, f"Result: {data.get('result', 'No result')}")
                return success
            else:
                self.log_test("Agent Execution", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Agent Execution", False, str(e))
            return False
    
    def test_workflow_execution(self) -> bool:
        """Test workflow execution endpoint."""
        try:
            payload = {
                "workflow_type": "research",
                "parameters": {
                    "query": "Test research query",
                    "max_results": 10
                }
            }
            response = requests.post(f"{self.base_url}/api/workflows/execute", json=payload, timeout=60)
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                self.log_test("Workflow Execution", success, f"Workflow: {data.get('workflow_type')}")
                return success
            else:
                self.log_test("Workflow Execution", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Workflow Execution", False, str(e))
            return False
    
    def test_memory_endpoints(self) -> bool:
        """Test memory-related endpoints."""
        try:
            # Test memory stats
            response = requests.get(f"{self.base_url}/api/memory/stats", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Memory Stats", True, f"Memory system available: {data.get('new_system', {}).get('conversation_memory_available', False)}")
            else:
                self.log_test("Memory Stats", False, f"Status code: {response.status_code}")
                return False
            
            # Test knowledge search
            response = requests.get(f"{self.base_url}/api/knowledge/search?q=test", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Knowledge Search", True, f"Query: {data.get('query')}")
            else:
                self.log_test("Knowledge Search", False, f"Status code: {response.status_code}")
                return False
            
            return True
        except Exception as e:
            self.log_test("Memory Endpoints", False, str(e))
            return False
    
    def test_security_endpoints(self) -> bool:
        """Test security-related endpoints."""
        try:
            # Test security stats
            response = requests.get(f"{self.base_url}/api/security/stats", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Security Stats", True, f"Bridge available: {data.get('bridge_available', False)}")
            else:
                self.log_test("Security Stats", False, f"Status code: {response.status_code}")
                return False
            
            # Test security audit
            response = requests.post(f"{self.base_url}/api/security/audit", timeout=30)
            if response.status_code == 200:
                data = response.json()
                status = data.get("status", "unknown")
                self.log_test("Security Audit", True, f"Status: {status}")
            else:
                self.log_test("Security Audit", False, f"Status code: {response.status_code}")
                return False
            
            return True
        except Exception as e:
            self.log_test("Security Endpoints", False, str(e))
            return False
    
    def test_monitoring_endpoints(self) -> bool:
        """Test monitoring-related endpoints."""
        try:
            # Test health status
            response = requests.get(f"{self.base_url}/api/monitoring/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                overall_status = data.get("overall_status", "unknown")
                self.log_test("Monitoring Health", True, f"Overall status: {overall_status}")
            else:
                self.log_test("Monitoring Health", False, f"Status code: {response.status_code}")
                return False
            
            # Test metrics
            response = requests.get(f"{self.base_url}/api/monitoring/metrics", timeout=10)
            if response.status_code == 200:
                data = response.json()
                metrics = data.get("metrics", [])
                self.log_test("Monitoring Metrics", True, f"Collected {len(metrics)} metrics")
            else:
                self.log_test("Monitoring Metrics", False, f"Status code: {response.status_code}")
                return False
            
            return True
        except Exception as e:
            self.log_test("Monitoring Endpoints", False, str(e))
            return False
    
    def test_websocket_connection(self) -> bool:
        """Test WebSocket connection."""
        try:
            import websocket
            import threading
            
            def on_message(ws, message):
                data = json.loads(message)
                if data.get("type") == "pong":
                    self.log_test("WebSocket Connection", True, "Pong received")
                    ws.close()
            
            def on_error(ws, error):
                self.log_test("WebSocket Connection", False, str(error))
            
            def on_close(ws, close_status_code, close_msg):
                pass
            
            def on_open(ws):
                ws.send(json.dumps({"type": "ping"}))
            
            ws = websocket.WebSocketApp(
                f"{self.base_url.replace('http', 'ws')}/ws/test_client",
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
                on_open=on_open
            )
            
            # Run WebSocket in a separate thread
            wst = threading.Thread(target=ws.run_forever)
            wst.daemon = True
            wst.start()
            
            # Wait for completion
            time.sleep(2)
            return True
            
        except ImportError:
            self.log_test("WebSocket Connection", False, "websocket-client not installed")
            return False
        except Exception as e:
            self.log_test("WebSocket Connection", False, str(e))
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests."""
        print("🧪 Starting Jarvis AI Integration Tests")
        print("=" * 50)
        
        # Core functionality tests
        self.test_health_endpoint()
        self.test_models_endpoint()
        self.test_agents_endpoint()
        self.test_chat_endpoint()
        
        # Advanced functionality tests
        self.test_agent_execution()
        self.test_workflow_execution()
        self.test_memory_endpoints()
        self.test_security_endpoints()
        self.test_monitoring_endpoints()
        
        # Connection tests
        self.test_websocket_connection()
        
        # Summary
        total_tests = len(self.results)
        passed_tests = total_tests - len(self.failed_tests)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print("\n" + "=" * 50)
        print(f"📊 Test Summary: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        
        if self.failed_tests:
            print(f"❌ Failed tests: {', '.join(self.failed_tests)}")
        else:
            print("🎉 All tests passed!")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": len(self.failed_tests),
            "success_rate": success_rate,
            "failed_test_names": self.failed_tests,
            "results": self.results
        }

def main():
    """Main test function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Jarvis AI Integration Test Suite")
    parser.add_argument("--url", default="http://127.0.0.1:8000", help="Base URL for API")
    parser.add_argument("--output", help="Output file for test results")
    
    args = parser.parse_args()
    
    tester = IntegrationTester(args.url)
    results = tester.run_all_tests()
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"📄 Test results saved to {args.output}")
    
    # Exit with error code if tests failed
    if results["failed_tests"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
