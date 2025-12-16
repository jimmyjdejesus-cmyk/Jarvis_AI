#!/usr/bin/env python3
"""
Standalone Test Server for Jarvis AI API Testing

This server provides all the endpoints needed for comprehensive API testing
without the dependency issues of the full Jarvis implementation.
"""

import json
import time
import asyncio
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading


class TestAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for test server."""
    
    # In-memory storage for testing
    personas = {
        "generalist": {
            "name": "generalist",
            "description": "Balanced assistant persona",
            "system_prompt": "You are a helpful assistant.",
            "max_context_window": 4096,
            "routing_hint": "general"
        },
        "researcher": {
            "name": "researcher",
            "description": "Deep research persona",
            "system_prompt": "Focus on sourcing and multi-step reasoning.",
            "max_context_window": 4096,
            "routing_hint": "research"
        }
    }
    
    allowed_personas = ["generalist", "researcher"]
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def send_cors_headers(self):
        """Send CORS headers."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-API-Key')
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            if path == "/health":
                self.handle_health()
            elif path == "/api/v1/models":
                self.handle_models()
            elif path == "/api/v1/personas":
                self.handle_personas()
            elif path == "/api/v1/monitoring/metrics":
                self.handle_metrics()
            elif path == "/api/v1/monitoring/traces":
                self.handle_traces()
            elif path == "/api/v1/management/system/status":
                self.handle_system_status()
            elif path == "/api/v1/management/routing/config":
                self.handle_routing_config()
            elif path == "/api/v1/management/backends":
                self.handle_backends()
            elif path == "/api/v1/management/context/config":
                self.handle_context_config()
            elif path == "/api/v1/management/security/status":
                self.handle_security_status()
            elif path == "/v1/models":
                self.handle_openai_models()
            else:
                self.send_error(404, "Not Found")
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {str(e)}")
    
    def do_POST(self):
        """Handle POST requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            if path == "/api/v1/chat":
                self.handle_chat()
            elif path == "/api/v1/management/backends/ollama/test":
                self.handle_backend_test()
            elif path == "/api/v1/management/personas":
                self.handle_create_persona()
            elif path == "/api/v1/management/config/save":
                self.handle_save_config()
            elif path == "/v1/chat/completions":
                self.handle_openai_chat()
            else:
                self.send_error(404, "Not Found")
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {str(e)}")
    
    def do_PUT(self):
        """Handle PUT requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            if path == "/api/v1/management/config/routing":
                self.handle_update_routing_config()
            elif path == "/api/v1/management/config/context":
                self.handle_update_context_config()
            elif path.startswith("/api/v1/management/personas/"):
                persona_name = path.split("/")[-1]
                self.handle_update_persona(persona_name)
            else:
                self.send_error(404, "Not Found")
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {str(e)}")
    
    def do_DELETE(self):
        """Handle DELETE requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            if path.startswith("/api/v1/management/personas/"):
                persona_name = path.split("/")[-1]
                self.handle_delete_persona(persona_name)
            else:
                self.send_error(404, "Not Found")
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {str(e)}")
    
    def handle_health(self):
        """Health check endpoint."""
        self.send_json_response({
            "status": "ok",
            "available_models": ["ollama", "openrouter", "test"]
        })
    
    def handle_models(self):
        """List models endpoint."""
        self.send_json_response(["ollama", "openrouter", "test-model"])
    
    def handle_personas(self):
        """List personas endpoint."""
        personas_list = []
        for name, persona in self.personas.items():
            persona_copy = persona.copy()
            persona_copy["is_active"] = name in self.allowed_personas
            personas_list.append(persona_copy)
        self.send_json_response(personas_list)
    
    def handle_chat(self):
        """Chat completion endpoint."""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            
            # Validate persona
            if data.get('persona') not in self.personas:
                self.send_error(400, f"Persona '{data.get('persona')}' not found")
                return
            
            # Mock response
            response = {
                "content": f"Test response from {data.get('persona', 'generalist')} persona. This is a mock response for API testing.",
                "model": "test-model",
                "tokens": 42,
                "diagnostics": {"backend": "test", "response_time_ms": 123.45}
            }
            self.send_json_response(response)
            
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
    
    def handle_metrics(self):
        """Metrics endpoint."""
        self.send_json_response({
            "history": [
                {
                    "request_count": 150,
                    "average_latency_ms": 245.6,
                    "max_latency_ms": 890.2,
                    "tokens_generated": 5000,
                    "context_tokens": 12000,
                    "personas_used": ["generalist", "researcher"]
                }
            ]
        })
    
    def handle_traces(self):
        """Traces endpoint."""
        self.send_json_response({
            "traces": [
                {
                    "persona": "generalist",
                    "backend": "test",
                    "latency_ms": 234.5,
                    "tokens": 50,
                    "timestamp": datetime.now().isoformat()
                }
            ]
        })
    
    def handle_system_status(self):
        """System status endpoint."""
        self.send_json_response({
            "status": "healthy",
            "uptime_seconds": 3600.5,
            "version": "1.0.0-test",
            "active_backends": ["ollama", "openrouter"],
            "active_personas": self.allowed_personas,
            "config_hash": "abc123def456"
        })
    
    def handle_routing_config(self):
        """Routing config endpoint."""
        self.send_json_response({
            "allowed_personas": self.allowed_personas,
            "enable_adaptive_routing": True
        })
    
    def handle_update_routing_config(self):
        """Update routing config endpoint."""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            
            if "allowed_personas" in data:
                self.allowed_personas = data["allowed_personas"]
            
            self.send_json_response({
                "allowed_personas": self.allowed_personas,
                "enable_adaptive_routing": data.get("enable_adaptive_routing", True)
            })
            
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
    
    def handle_backends(self):
        """List backends endpoint."""
        self.send_json_response({
            "backends": [
                {
                    "name": "ollama",
                    "type": "ollama",
                    "is_available": True,
                    "last_checked": time.time(),
                    "config": {}
                },
                {
                    "name": "openrouter",
                    "type": "openrouter",
                    "is_available": False,
                    "last_checked": time.time(),
                    "config": {"api_key": "***"}
                }
            ]
        })
    
    def handle_backend_test(self):
        """Test backend endpoint."""
        self.send_json_response({
            "success": True,
            "latency_ms": 45.2,
            "error": None
        })
    
    def handle_context_config(self):
        """Context config endpoint."""
        self.send_json_response({
            "extra_documents_dir": None,
            "enable_semantic_chunking": True,
            "max_combined_context_tokens": 8192
        })
    
    def handle_update_context_config(self):
        """Update context config endpoint."""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            self.send_json_response({
                "extra_documents_dir": data.get("extra_documents_dir"),
                "enable_semantic_chunking": data.get("enable_semantic_chunking", True),
                "max_combined_context_tokens": data.get("max_combined_context_tokens", 8192)
            })
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
    
    def handle_security_status(self):
        """Security status endpoint."""
        self.send_json_response({
            "api_keys_count": 0,
            "audit_log_enabled": False
        })
    
    def handle_create_persona(self):
        """Create persona endpoint."""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            
            persona_name = data.get("name")
            if persona_name in self.personas:
                self.send_error(400, "Persona already exists")
                return
            
            persona = {
                "name": persona_name,
                "description": data.get("description", ""),
                "system_prompt": data.get("system_prompt", ""),
                "max_context_window": data.get("max_context_window", 4096),
                "routing_hint": data.get("routing_hint", "general"),
                "is_active": True
            }
            
            self.personas[persona_name] = persona
            self.allowed_personas.append(persona_name)
            
            self.send_json_response(persona)
            
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
    
    def handle_update_persona(self, persona_name):
        """Update persona endpoint."""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            
            if persona_name not in self.personas:
                self.send_error(404, "Persona not found")
                return
            
            persona = self.personas[persona_name]
            for key, value in data.items():
                if key in ["description", "system_prompt", "max_context_window", "routing_hint"]:
                    persona[key] = value
            
            persona["is_active"] = persona_name in self.allowed_personas
            self.send_json_response(persona)
            
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
    
    def handle_delete_persona(self, persona_name):
        """Delete persona endpoint."""
        if persona_name not in self.personas:
            self.send_error(404, "Persona not found")
            return
        
        if persona_name in ["generalist", "researcher"]:
            self.send_error(400, "Cannot delete default personas")
            return
        
        del self.personas[persona_name]
        if persona_name in self.allowed_personas:
            self.allowed_personas.remove(persona_name)
        
        self.send_json_response({"message": f"Persona '{persona_name}' deleted successfully"})
    
    def handle_save_config(self):
        """Save config endpoint."""
        self.send_json_response({
            "success": True,
            "config_hash": "abc123def456",
            "message": "Configuration saved successfully"
        })
    
    def handle_openai_chat(self):
        """OpenAI-compatible chat completions endpoint."""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            
            # Mock OpenAI response
            response = {
                "id": f"chatcmpl-{int(time.time())}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": "test-model",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "This is a test response from the OpenAI-compatible endpoint."
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 15,
                    "total_tokens": 25
                }
            }
            
            self.send_json_response(response)
            
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
    
    def handle_openai_models(self):
        """OpenAI-compatible models endpoint."""
        self.send_json_response({
            "object": "list",
            "data": [
                {
                    "id": "test-model",
                    "object": "model",
                    "created": int(time.time()),
                    "owned_by": "jarvis"
                }
            ]
        })
    
    def send_json_response(self, data):
        """Send JSON response."""
        response_body = json.dumps(data, indent=2).encode('utf-8')
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.send_header('Content-Length', str(len(response_body)))
        self.end_headers()
        self.wfile.write(response_body)
    
    def log_message(self, format, *args):
        """Override to customize logging."""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")


def start_test_server(port=8000):
    """Start the test server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, TestAPIHandler)
    
    print(f"🚀 Test server starting on port {port}")
    print(f"🔗 Health check: http://127.0.0.1:{port}/health")
    print(f"📖 API docs: http://127.0.0.1:{port}/docs")
    print("✅ Server ready for API testing")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Test server stopped")
        httpd.shutdown()


if __name__ == "__main__":
    start_test_server()
