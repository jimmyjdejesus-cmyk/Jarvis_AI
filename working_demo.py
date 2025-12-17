# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/




Copyright (c) 2025 Jimmy De Jesus (Bravetto)

Licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0).
See https://creativecommons.org/licenses/by/4.0/ for license terms.

#!/usr/bin/env python3
"""
Working Jarvis demonstration with fixed router.
This script demonstrates a fully functional Jarvis assistant.
"""

import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from jarvis_core.app import JarvisApplication
from jarvis_core.config import load_config
from jarvis_core.routing.router_fixed import AdaptiveLLMRouter

class JarvisDemoHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, jarvis_app=None, **kwargs):
        self.jarvis_app = jarvis_app
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == "/":
            self._send_response(200, _INDEX_HTML, "text/html")
        elif self.path == "/health":
            self._handle_health()
        else:
            self._send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == "/api/v1/chat":
            self._handle_chat()
        else:
            self._send_error(404, "Not Found")
    
    def _handle_health(self):
        """Handle health check endpoint"""
        try:
            models = self.jarvis_app.models()
            response_data = {
                "status": "ok" if models else "degraded",
                "available_models": models
            }
            self._send_json_response(response_data)
        except Exception as e:
            self._send_error(500, f"Health check failed: {str(e)}")
    
    def _handle_chat(self):
        """Handle chat endpoint"""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self._send_error(400, "Missing request body")
                return
            
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            # Extract parameters
            messages = request_data.get('messages', [])
            persona = request_data.get('persona', 'generalist')
            temperature = request_data.get('temperature', 0.7)
            max_tokens = request_data.get('max_tokens', 512)
            
            # Generate response using our fixed router
            payload = self.jarvis_app.chat(
                persona=persona,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            self._send_json_response(payload)
            
        except Exception as e:
            self._send_error(500, f"Chat request failed: {str(e)}")
    
    def _send_json_response(self, data, status_code=200):
        """Send JSON response"""
        response_body = json.dumps(data, indent=2)
        self._send_response(status_code, response_body, "application/json")
    
    def _send_response(self, status_code, content, content_type):
        """Send response with content"""
        self.send_response(status_code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(content.encode('utf-8'))))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))
    
    def _send_error(self, status_code, message):
        """Send error response"""
        response_data = {"error": message}
        self._send_json_response(response_data, status_code)
    
    def log_message(self, format, *args):
        """Override to customize logging"""
        print(f"[{self.address_string()}] {format % args}")

def create_handler_class(jarvis_app):
    """Create a handler class with the Jarvis app instance"""
    class BoundHandler(JarvisDemoHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, jarvis_app=jarvis_app, **kwargs)
    return BoundHandler

def run_demo_server():
    """Run the working Jarvis demonstration server"""
    print("🤖 Starting Working Jarvis Demonstration...")
    print("=" * 60)
    
    # Initialize Jarvis with fixed configuration
    config = load_config()
    jarvis_app = JarvisApplication(config=config)
    
    # Replace router with fixed version to handle empty allowed_personas
    jarvis_app.router = AdaptiveLLMRouter(
        config=config,
        context_engine=jarvis_app.context_engine,
        backends=jarvis_app.backends,
        metrics=jarvis_app.metrics,
        traces=jarvis_app.traces,
    )
    
    print(f"✅ Jarvis application initialized with fixed router")
    print(f"📊 Available backends: {len(jarvis_app.backends)}")
    print(f"🎭 Configured personas: {list(jarvis_app.config.personas.keys())}")
    print(f"📈 Models available: {jarvis_app.models()}")
    
    # Test the chat functionality
    print("\n🧪 Testing chat functionality...")
    try:
        test_response = jarvis_app.chat(
            'generalist', 
            [{'role': 'user', 'content': 'Hello, this is a test message!'}]
        )
        print(f"✅ Chat test successful!")
        print(f"📝 Response: {test_response['content'][:100]}...")
        print(f"🤖 Model: {test_response['model']}")
        print(f"📊 Tokens: {test_response['tokens']}")
    except Exception as e:
        print(f"❌ Chat test failed: {e}")
    
    # Create and start server
    handler_class = create_handler_class(jarvis_app)
    server = HTTPServer(("127.0.0.1", 8000), handler_class)
    
    print(f"\n🚀 Server running at http://127.0.0.1:8000")
    print(f"🌐 Open your browser to: http://127.0.0.1:8000")
    print("📝 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down server...")
        server.shutdown()
        jarvis_app.shutdown()
        print("✅ Server stopped")

_INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>🤖 Jarvis Working Demo</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 2rem; 
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); 
            color: #fff; 
            min-height: 100vh; 
        }
        .container { 
            max-width: 800px; 
            margin: 0 auto; 
            background: rgba(255, 255, 255, 0.1); 
            padding: 2rem; 
            border-radius: 16px; 
            backdrop-filter: blur(10px);
        }
        h1 { 
            text-align: center; 
            color: #00e0ff; 
            margin-bottom: 2rem;
            font-size: 2.5rem;
        }
        .status { 
            margin-bottom: 1.5rem; 
            padding: 1rem; 
            border-radius: 8px; 
            text-align: center;
            background: rgba(0, 255, 0, 0.2);
            border: 1px solid rgba(0, 255, 0, 0.3);
        }
        textarea { 
            width: 100%; 
            height: 100px; 
            padding: 1rem; 
            background: rgba(255, 255, 255, 0.1); 
            color: #fff; 
            border: 1px solid rgba(255, 255, 255, 0.3); 
            border-radius: 8px; 
            resize: vertical;
            font-size: 1rem;
        }
        button { 
            padding: 1rem 2rem; 
            margin-top: 1rem; 
            background: #00e0ff; 
            color: #000; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer; 
            font-size: 1rem; 
            font-weight: bold;
        }
        button:hover { 
            background: #00b8d4; 
        }
        pre { 
            white-space: pre-wrap; 
            background: rgba(0, 0, 0, 0.3); 
            padding: 1rem; 
            border-radius: 8px; 
            margin-top: 1rem;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Jarvis Working Demo</h1>
        <div id="status" class="status">✅ System Ready - Fixed Router Active!</div>
        
        <textarea id="prompt" placeholder="Ask Jarvis anything..."></textarea>
        <button onclick="sendChat()">Send Message</button>
        <pre id="output">Ready to chat!</pre>
    </div>

    <script>
        async function sendChat() {
            const prompt = document.getElementById('prompt').value.trim();
            if (!prompt) return;
            
            const output = document.getElementById('output');
            output.textContent = 'Thinking...';
            
            try {
                const response = await fetch('/api/v1/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        persona: 'generalist',
                        messages: [{ role: 'user', content: prompt }]
                    })
                });
                
                const data = await response.json();
                output.textContent = data.content + '\\n\\nModel: ' + data.model + ' | Tokens: ' + data.tokens;
                
            } catch (error) {
                output.textContent = 'Error: ' + error.message;
            }
        }
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    run_demo_server()
