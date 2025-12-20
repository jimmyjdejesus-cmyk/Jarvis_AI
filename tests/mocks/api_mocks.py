# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/

"""Mock implementations for HTTP/API clients and responses.

This module provides comprehensive mock objects for HTTP clients,
API responses, and web socket functionality to enable isolated
testing without real network dependencies.
"""

import time
import json
from unittest.mock import Mock
from typing import Dict, List, Any, Optional


class MockHTTPResponse:
    """Mock HTTP response for testing."""
    
    def __init__(self, data: Any = None, status_code: int = 200, 
                 headers: Optional[Dict[str, str]] = None, 
                 elapsed_seconds: float = 0.01):
        self.status_code = status_code
        self.headers = headers or {"Content-Type": "application/json"}
        self._data = data or {}
        self.elapsed = Mock()
        self.elapsed.total_seconds.return_value = elapsed_seconds
        self.text = str(self._data)
        
    def json(self) -> Any:
        """Return response data as JSON."""
        if isinstance(self._data, str):
            return json.loads(self._data)
        return self._data
    
    def raise_for_status(self):
        """Mock raise_for_status method."""
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code} Error")


class MockHTTPClient:
    """Mock HTTP client for API testing."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = Mock()
        self.timeout = 30
        self.headers = {}
        self.call_log = []
        
    def get(self, url: str, **kwargs) -> MockHTTPResponse:
        """Mock GET request."""
        self._log_call("GET", url, kwargs)
        return self._create_response("GET", url, kwargs)
    
    def post(self, url: str, **kwargs) -> MockHTTPResponse:
        """Mock POST request."""
        self._log_call("POST", url, kwargs)
        return self._create_response("POST", url, kwargs)
    
    def put(self, url: str, **kwargs) -> MockHTTPResponse:
        """Mock PUT request."""
        self._log_call("PUT", url, kwargs)
        return self._create_response("PUT", url, kwargs)
    
    def delete(self, url: str, **kwargs) -> MockHTTPResponse:
        """Mock DELETE request."""
        self._log_call("DELETE", url, kwargs)
        return self._create_response("DELETE", url, kwargs)
    
    def patch(self, url: str, **kwargs) -> MockHTTPResponse:
        """Mock PATCH request."""
        self._log_call("PATCH", url, kwargs)
        return self._create_response("PATCH", url, kwargs)
    
    def _log_call(self, method: str, url: str, kwargs: Dict):
        """Log API call for testing verification."""
        self.call_log.append({
            "method": method,
            "url": url,
            "kwargs": kwargs,
            "timestamp": time.time()
        })
    
    def _create_response(self, method: str, url: str, kwargs: Dict) -> MockHTTPResponse:
        """Create appropriate mock response based on endpoint."""
        # Default response
        default_response = {
            "status": "success",
            "timestamp": time.time(),
            "method": method,
            "endpoint": url
        }
        
        # Customize response based on endpoint patterns
        if "/chat/completions" in url:
            return MockHTTPResponse({
                "id": "chatcmpl-test-id",
                "object": "chat.completion", 
                "created": int(time.time()),
                "model": "llama3.2:latest",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Mock response from API"
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": 5,
                    "completion_tokens": 15,
                    "total_tokens": 20
                }
            })
        elif "/health" in url or "/status" in url:
            return MockHTTPResponse({
                "status": "healthy",
                "timestamp": time.time(),
                "uptime": 3600
            })
        elif "/jobs" in url:
            return MockHTTPResponse({
                "total_events": 0,
                "ingested": True,
                "job_id": "test-job-123",
                "status": "completed"
            })
        
        return MockHTTPResponse(default_response)
    
    def reset_log(self):
        """Reset call log for fresh testing."""
        self.call_log = []
    
    def get_last_call(self) -> Optional[Dict]:
        """Get the most recent API call."""
        return self.call_log[-1] if self.call_log else None
    
    def get_call_count(self) -> int:
        """Get total number of API calls made."""
        return len(self.call_log)


class MockWebSocket:
    """Mock WebSocket for testing."""
    
    def __init__(self, url: str = "ws://localhost:8000/ws"):
        self.url = url
        self.closed = False
        self.messages_sent = []
        self.messages_received = []
        self.on_message = None
        self.on_open = None
        self.on_close = None
        self.on_error = None
        
    async def send(self, message: str):
        """Mock sending a message."""
        if self.closed:
            raise Exception("WebSocket is closed")
        
        self.messages_sent.append({
            "type": "sent",
            "message": message,
            "timestamp": time.time()
        })
    
    async def receive(self) -> str:
        """Mock receiving a message."""
        if self.closed:
            raise Exception("WebSocket is closed")
        
        # Simulate receiving a response
        response = {
            "type": "assistant",
            "content": "Mock websocket response",
            "timestamp": time.time()
        }
        
        message_str = json.dumps(response)
        self.messages_received.append({
            "type": "received", 
            "message": message_str,
            "timestamp": time.time()
        })
        
        return message_str
    
    async def close(self):
        """Mock closing the WebSocket."""
        self.closed = True
        if self.on_close:
            self.on_close()
    
    def emit_message(self, message: str):
        """Simulate receiving a message from server."""
        self.messages_received.append({
            "type": "received",
            "message": message,
            "timestamp": time.time()
        })
        
        if self.on_message:
            self.on_message(message)


class MockAsyncHTTPClient:
    """Mock async HTTP client for testing."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = Mock()
        
    async def get(self, url: str, **kwargs) -> MockHTTPResponse:
        """Mock async GET request."""
        return MockHTTPResponse({"status": "success", "method": "GET"})
    
    async def post(self, url: str, **kwargs) -> MockHTTPResponse:
        """Mock async POST request."""
        return MockHTTPResponse({"status": "success", "method": "POST"})
    
    async def put(self, url: str, **kwargs) -> MockHTTPResponse:
        """Mock async PUT request."""
        return MockHTTPResponse({"status": "success", "method": "PUT"})
    
    async def delete(self, url: str, **kwargs) -> MockHTTPResponse:
        """Mock async DELETE request."""
        return MockHTTPResponse({"status": "success", "method": "DELETE"})


class MockRequestsModule:
    """Mock requests module for testing."""
    
    def __init__(self):
        self.get = Mock(side_effect=self._mock_get)
        self.post = Mock(side_effect=self._mock_post)
        self.put = Mock(side_effect=self._mock_put)
        self.delete = Mock(side_effect=self._mock_delete)
        self.patch = Mock(side_effect=self._mock_patch)
        self.Session = Mock()
        self.exceptions = self._create_exceptions()
    
    def _mock_get(self, url: str, **kwargs) -> MockHTTPResponse:
        """Mock GET request."""
        return MockHTTPResponse({"method": "GET", "url": url})
    
    def _mock_post(self, url: str, **kwargs) -> MockHTTPResponse:
        """Mock POST request."""
        return MockHTTPResponse({"method": "POST", "url": url})
    
    def _mock_put(self, url: str, **kwargs) -> MockHTTPResponse:
        """Mock PUT request."""
        return MockHTTPResponse({"method": "PUT", "url": url})
    
    def _mock_delete(self, url: str, **kwargs) -> MockHTTPResponse:
        """Mock DELETE request."""
        return MockHTTPResponse({"method": "DELETE", "url": url})
    
    def _mock_patch(self, url: str, **kwargs) -> MockHTTPResponse:
        """Mock PATCH request."""
        return MockHTTPResponse({"method": "PATCH", "url": url})
    
    def _create_exceptions(self):
        """Create mock exception classes."""
        exceptions = Mock()
        
        class MockRequestException(Exception):
            pass
        
        class MockConnectionError(MockRequestException):
            pass
        
        class MockTimeout(MockRequestException):
            pass
        
        class MockHTTPError(MockRequestException):
            pass
        
        class MockRetryError(MockRequestException):
            pass
        
        exceptions.RequestException = MockRequestException
        exceptions.ConnectionError = MockConnectionError
        exceptions.Timeout = MockTimeout
        exceptions.HTTPError = MockHTTPError
        exceptions.RetryError = MockRetryError
        
        return exceptions


# Setup module-level requests mock
def setup_requests_mock():
    """Setup requests module mock to prevent import errors."""
    import sys
    import types
    
    requests_module = types.ModuleType("requests")
    mock_requests = MockRequestsModule()
    
    requests_module.get = mock_requests.get
    requests_module.post = mock_requests.post
    requests_module.put = mock_requests.put
    requests_module.delete = mock_requests.delete
    requests_module.patch = mock_requests.patch
    requests_module.Session = mock_requests.Session
    requests_module.exceptions = mock_requests.exceptions
    
    # Setup adapters module
    adapters_module = types.ModuleType("adapters")
    
    class MockHTTPAdapter:
        def send(self, *args, **kwargs):
            return MockHTTPResponse()
    
    class MockMaxRetryError(Exception):
        pass
    
    adapters_module.HTTPAdapter = MockHTTPAdapter
    adapters_module.MaxRetryError = MockMaxRetryError
    requests_module.adapters = adapters_module
    
    sys.modules.setdefault("requests", requests_module)
    sys.modules.setdefault("requests.adapters", adapters_module)
    sys.modules.setdefault("requests.exceptions", mock_requests.exceptions)


# Initialize mocks on import
setup_requests_mock()

__all__ = [
    "MockHTTPResponse",
    "MockHTTPClient", 
    "MockWebSocket",
    "MockAsyncHTTPClient",
    "MockRequestsModule",
    "setup_requests_mock"
]
