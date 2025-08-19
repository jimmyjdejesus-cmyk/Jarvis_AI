"""
Enhanced Testing Framework for Jarvis AI
Provides comprehensive testing capabilities including unit tests, integration tests, and system tests.
"""

import unittest
import pytest
import time
import os
import tempfile
import shutil
from typing import Dict, Any, List, Optional, Callable
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass
import json

from agent.core.error_handling import get_logger, get_error_handler
from agent.core.config_manager import get_config_manager, JarvisConfig
from agent.core.performance_monitor import get_performance_monitor


@dataclass
class TestResult:
    """Test result data structure."""
    test_name: str
    passed: bool
    duration: float
    error_message: Optional[str] = None
    details: Dict[str, Any] = None


class JarvisTestCase(unittest.TestCase):
    """Enhanced test case base class with additional utilities."""
    
    def setUp(self):
        """Set up test environment."""
        self.logger = get_logger()
        self.temp_dir = tempfile.mkdtemp()
        self.config_manager = get_config_manager()
        self.performance_monitor = get_performance_monitor()
        
        # Create test configuration
        self.test_config = JarvisConfig()
        self.test_config.debug_mode = True
        self.test_config.data_directory = self.temp_dir
        self.test_config.logs_directory = os.path.join(self.temp_dir, "logs")
    
    def tearDown(self):
        """Clean up test environment."""
        try:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass
    
    def assertPerformance(self, func: Callable, max_duration: float, *args, **kwargs):
        """Assert that a function completes within a time limit."""
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        
        self.assertLessEqual(
            duration, max_duration,
            f"Function {func.__name__} took {duration:.3f}s, expected <= {max_duration}s"
        )
        return result
    
    def assertNoErrors(self, func: Callable, *args, **kwargs):
        """Assert that a function doesn't raise any exceptions."""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.fail(f"Function {func.__name__} raised unexpected exception: {e}")
    
    def assertErrorLogged(self, expected_error_type: type, func: Callable, *args, **kwargs):
        """Assert that a specific error type is logged when function is called."""
        error_handler = get_error_handler()
        initial_count = error_handler.error_count.get(expected_error_type, 0)
        
        try:
            func(*args, **kwargs)
        except:
            pass  # We're testing error logging, not whether exception is raised
        
        final_count = error_handler.error_count.get(expected_error_type, 0)
        self.assertGreater(
            final_count, initial_count,
            f"Expected {expected_error_type.__name__} to be logged"
        )
    
    def create_test_file(self, content: str, filename: str = "test_file.txt") -> str:
        """Create a temporary test file."""
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        return filepath
    
    def mock_ollama_response(self, response_text: str = "Test response"):
        """Mock Ollama API response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": response_text}
        return mock_response


class SystemTestSuite:
    """Comprehensive system test suite."""
    
    def __init__(self):
        self.logger = get_logger()
        self.results: List[TestResult] = []
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all system tests."""
        self.logger.logger.info("Starting comprehensive system tests...")
        
        test_methods = [
            ("Configuration Tests", self._test_configuration),
            ("Plugin System Tests", self._test_plugin_system),
            ("RAG System Tests", self._test_rag_system),
            ("Error Handling Tests", self._test_error_handling),
            ("Performance Tests", self._test_performance),
            ("Integration Tests", self._test_integrations),
            ("Security Tests", self._test_security)
        ]
        
        for test_name, test_method in test_methods:
            try:
                start_time = time.time()
                test_method()
                duration = time.time() - start_time
                
                self.results.append(TestResult(
                    test_name=test_name,
                    passed=True,
                    duration=duration
                ))
                self.logger.logger.info(f"✅ {test_name} passed ({duration:.2f}s)")
                
            except Exception as e:
                duration = time.time() - start_time
                self.results.append(TestResult(
                    test_name=test_name,
                    passed=False,
                    duration=duration,
                    error_message=str(e)
                ))
                self.logger.logger.error(f"❌ {test_name} failed: {e}")
        
        return self._generate_test_report()
    
    def _test_configuration(self):
        """Test configuration management."""
        config_manager = get_config_manager()
        
        # Test loading default config
        config = config_manager.load_config()
        assert config is not None, "Config should not be None"
        
        # Test updating config
        updates = {"debug_mode": True, "custom": {"test_key": "test_value"}}
        config_manager.update_config(updates)
        updated_config = config_manager.get_config()
        assert updated_config.debug_mode == True, "Debug mode should be updated"
        assert updated_config.custom["test_key"] == "test_value", "Custom config should be updated"
    
    def _test_plugin_system(self):
        """Test plugin system functionality."""
        try:
            from agent.adapters.plugin_registry import plugin_manager
            from agent.adapters.plugin_base import BasePlugin, PluginMetadata, PluginType
            
            # Test plugin creation and registration
            class TestPlugin(BasePlugin):
                def __init__(self):
                    super().__init__(PluginMetadata(
                        name="TestPlugin",
                        version="1.0.0",
                        description="Test plugin",
                        plugin_type=PluginType.AUTOMATION,
                        triggers=["test command"]
                    ))
                
                def execute(self, action, context=None):
                    return {"success": True, "message": "Test executed"}
            
            test_plugin = TestPlugin()
            success = plugin_manager.registry.register_plugin(test_plugin)
            assert success, "Plugin registration should succeed"
            
            # Test plugin discovery
            plugins = plugin_manager.registry.find_plugins_for_command("test command")
            assert len(plugins) > 0, "Should find registered plugin"
            
        except ImportError as e:
            raise Exception(f"Plugin system imports failed: {e}")
    
    def _test_rag_system(self):
        """Test RAG system functionality."""
        try:
            from agent.features.rag_handler import rag_answer, extract_file_content
            
            # Test file content extraction
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
                f.write("Test file content for RAG testing")
                test_file = f.name
            
            try:
                content = extract_file_content(test_file)
                assert "Test file content" in content, "Should extract file content"
                
                # Test RAG with file context
                result = rag_answer("What is in this file?", [test_file], mode="file")
                assert isinstance(result, str), "RAG should return string result"
                assert len(result) > 0, "RAG result should not be empty"
                
            finally:
                os.unlink(test_file)
                
        except ImportError as e:
            raise Exception(f"RAG system imports failed: {e}")
    
    def _test_error_handling(self):
        """Test error handling system."""
        from agent.core.error_handling import robust_operation, get_error_handler
        
        # Test error handler
        error_handler = get_error_handler()
        
        # Create a test error
        test_error = ValueError("Test error")
        error_info = error_handler.handle_error(test_error, {"test": "context"})
        
        assert error_info["error_type"] == "ValueError", "Should capture error type"
        assert "Test error" in error_info["error_message"], "Should capture error message"
        
        # Test robust operation decorator
        @robust_operation(max_retries=2)
        def failing_function():
            raise Exception("Always fails")
        
        try:
            failing_function()
            assert False, "Should have raised exception"
        except Exception:
            pass  # Expected
        
        # Check error statistics
        stats = error_handler.get_error_statistics()
        assert stats["total_errors"] > 0, "Should have recorded errors"
    
    def _test_performance(self):
        """Test performance monitoring."""
        from agent.core.performance_monitor import get_performance_monitor, performance_monitor
        
        perf_monitor = get_performance_monitor()
        
        # Test metric recording
        perf_monitor.record_metric("test.metric", 42.0, "units")
        recent_metrics = perf_monitor.get_recent_metrics(1)
        assert len(recent_metrics) > 0, "Should have recorded metrics"
        
        # Test operation monitoring
        @performance_monitor("test_operation")
        def test_operation():
            time.sleep(0.1)
            return "success"
        
        result = test_operation()
        assert result == "success", "Operation should complete successfully"
        
        stats = perf_monitor.get_operation_stats("test_operation")
        assert stats["total_calls"] > 0, "Should have recorded operation stats"
        
        # Test health check
        health = perf_monitor.get_system_health()
        assert "status" in health, "Health check should return status"
        assert "checks" in health, "Health check should include detailed checks"
    
    def _test_integrations(self):
        """Test external integrations."""
        # Test basic import capabilities
        integration_modules = [
            "requests",  # For API calls
            "yaml",      # For configuration
            "json",      # For data handling
        ]
        
        for module_name in integration_modules:
            try:
                __import__(module_name)
            except ImportError:
                raise Exception(f"Required integration module '{module_name}' not available")
        
        # Test Ollama connectivity (if available)
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                self.logger.logger.info("Ollama service is available")
            else:
                self.logger.logger.warning("Ollama service returned non-200 status")
        except:
            self.logger.logger.warning("Ollama service not available (expected in test environment)")
    
    def _test_security(self):
        """Test security features."""
        from agent.core.config_manager import get_config
        
        config = get_config()
        
        # Check security configuration
        assert len(config.security.cookie_secret_key) >= 16, "Cookie secret should be at least 16 chars"
        assert config.security.password_min_length >= 6, "Password min length should be reasonable"
        assert config.security.max_login_attempts > 0, "Should have login attempt limits"
        
        # Test that sensitive data is not exposed in logs
        # This is a basic check - more comprehensive security testing would be needed
        assert "password" not in str(config).lower() or "***" in str(config), "Passwords should be masked"
    
    def _generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        passed_tests = [r for r in self.results if r.passed]
        failed_tests = [r for r in self.results if not r.passed]
        
        report = {
            "timestamp": time.time(),
            "summary": {
                "total_tests": len(self.results),
                "passed": len(passed_tests),
                "failed": len(failed_tests),
                "success_rate": len(passed_tests) / max(len(self.results), 1),
                "total_duration": sum(r.duration for r in self.results)
            },
            "results": [
                {
                    "test_name": r.test_name,
                    "passed": r.passed,
                    "duration": r.duration,
                    "error_message": r.error_message
                }
                for r in self.results
            ],
            "failed_tests": [
                {
                    "test_name": r.test_name,
                    "error": r.error_message,
                    "duration": r.duration
                }
                for r in failed_tests
            ]
        }
        
        return report


def run_quick_tests() -> bool:
    """Run a quick subset of tests for basic functionality verification."""
    try:
        # Test basic imports first
        from agent.core.error_handling import get_logger
        from agent.core.config_manager import get_config
        from agent.core.performance_monitor import get_performance_monitor
        
        logger = get_logger()
        logger.logger.info("Running quick system tests...")
        
        # Test basic functionality
        config = get_config()
        assert config is not None, "Config should be available"
        
        logger.logger.info("✅ Quick tests passed")
        return True
        
    except Exception as e:
        logger.logger.error(f"❌ Quick tests failed: {e}")
        return False


def run_comprehensive_tests() -> Dict[str, Any]:
    """Run comprehensive system tests."""
    test_suite = SystemTestSuite()
    return test_suite.run_all_tests()


if __name__ == "__main__":
    # Run tests when module is executed directly
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        success = run_quick_tests()
        sys.exit(0 if success else 1)
    else:
        report = run_comprehensive_tests()
        print(json.dumps(report, indent=2))
        sys.exit(0 if report["summary"]["failed"] == 0 else 1)