#!/usr/bin/env python3

# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



"""
Simple standalone HTTP server for Jarvis demonstration.
This bypasses all FastAPI middleware issues by using Python's built-in HTTP server.
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from jarvis_core.app import JarvisApplication
from jarvis_core.config import load_config

class JarvisHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, jarvis_app=None, **kwargs):
        self.jarvis_app = jarvis_app
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == "/":
            self._send_html_response(_INDEX_HTML)
        elif path == "/health":
            self._handle_health()
        elif path == "/api/v1/models":
            self._handle_models()
        else:
            self._send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == "/api/v1/chat":
            self._handle_chat()
        else:
            self._send_error(404, "Not Found")
    
    def _handle_health(self):
        """Handle health check endpoint"""
        try:
            models = self.jarvis_app.models()
            status_value = "ok" if models else "degraded"
            
            response_data = {
                "status": status_value,
                "available_models": models
            }
            self._send_json_response(response_data)
        except Exception as e:
            self._send_error(500, f"Health check failed: {str(e)}")
    
    def _handle_models(self):
        """Handle models endpoint"""
        try:
            models = self.jarvis_app.models()
            self._send_json_response(models)
        except Exception as e:
            self._send_error(500, f"Failed to get models: {str(e)}")
    
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
            
            # Validate persona
            if persona not in self.jarvis_app.config.personas:
                available_personas = list(self.jarvis_app.config.personas.keys())
                self._send_error(400, f"Persona '{persona}' not found. Available: {available_personas}")
                return
            
            # Generate response
            payload = self.jarvis_app.chat(
                persona=persona,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            # Return response
            self._send_json_response(payload)
            
        except json.JSONDecodeError:
            self._send_error(400, "Invalid JSON in request body")
        except Exception as e:
            self._send_error(500, f"Chat request failed: {str(e)}")
    
    def _send_json_response(self, data, status_code=200):
        """Send JSON response"""
        response_body = json.dumps(data, indent=2)
        
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response_body.encode('utf-8'))))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response_body.encode('utf-8'))
    
    def _send_html_response(self, html_content, status_code=200):
        """Send HTML response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', str(len(html_content.encode('utf-8'))))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def _send_error(self, status_code, message):
        """Send error response"""
        response_data = {"error": message}
        self._send_json_response(response_data, status_code)
    
    def log_message(self, format, *args):
        """Override to customize logging"""
        print(f"[{self.address_string()}] {format % args}")

def create_handler_class(jarvis_app):
    """Create a handler class with the Jarvis app instance"""
    class BoundHandler(JarvisHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, jarvis_app=jarvis_app, **kwargs)
    
    return BoundHandler

def run_server(host="127.0.0.1", port=8000):
    """Run the standalone Jarvis server"""
    print("🤖 Starting Jarvis Local Assistant...")
    print("=" * 50)
    
    # Initialize Jarvis application
    try:
        config = load_config()
        jarvis_app = JarvisApplication(config=config)
        print(f"✅ Jarvis application initialized")
        print(f"📊 Available backends: {len(jarvis_app.backends)}")
        print(f"🎭 Configured personas: {list(jarvis_app.config.personas.keys())}")
        print(f"📈 Models available: {jarvis_app.models()}")
    except Exception as e:
        print(f"❌ Failed to initialize Jarvis: {e}")
        return
    
    # Create handler class
    handler_class = create_handler_class(jarvis_app)
    
    # Create and start server
    try:
        server = HTTPServer((host, port), handler_class)
        print(f"🚀 Server running at http://{host}:{port}")
        print(f"🌐 Open your browser to: http://{host}:{port}")
        print("📝 Press Ctrl+C to stop the server")
        print("=" * 50)
        
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down server...")
        server.shutdown()
        jarvis_app.shutdown()
        print("✅ Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")

_INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>🤖 Jarvis Local Assistant</title>
    <style>
        * { box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            margin: 0; 
            padding: 0; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: #f8f9fa; 
            min-height: 100vh; 
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container { 
            max-width: 900px; 
            width: 90%; 
            background: rgba(255, 255, 255, 0.1); 
            padding: 2.5rem; 
            border-radius: 20px; 
            backdrop-filter: blur(15px); 
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        h1 { 
            text-align: center; 
            background: linear-gradient(45deg, #00e0ff, #00ff88);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 2rem; 
            font-size: 3rem;
            font-weight: 700;
        }
        .status { 
            margin-bottom: 2rem; 
            padding: 1rem 1.5rem; 
            border-radius: 12px; 
            text-align: center; 
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .status.ok { 
            background: linear-gradient(135deg, rgba(40, 167, 69, 0.2), rgba(32, 201, 151, 0.2)); 
            border: 1px solid rgba(40, 167, 69, 0.5);
            color: #d4edda;
        }
        .status.degraded { 
            background: linear-gradient(135deg, rgba(255, 193, 7, 0.2), rgba(253, 126, 20, 0.2)); 
            border: 1px solid rgba(255, 193, 7, 0.5);
            color: #fff3cd;
        }
        .status.error { 
            background: linear-gradient(135deg, rgba(220, 53, 69, 0.2), rgba(248, 69, 58, 0.2)); 
            border: 1px solid rgba(220, 53, 69, 0.5);
            color: #f8d7da;
        }
        .input-section {
            margin-bottom: 2rem;
        }
        label { 
            display: block; 
            margin-bottom: 0.8rem; 
            font-weight: 600; 
            color: #e9ecef;
            font-size: 1.1rem;
        }
        textarea { 
            width: 100%; 
            height: 120px; 
            padding: 1.2rem; 
            background: rgba(255, 255, 255, 0.1); 
            color: #f8f9fa; 
            border: 1px solid rgba(255, 255, 255, 0.3); 
            border-radius: 12px; 
            resize: vertical;
            font-size: 1rem;
            font-family: inherit;
            transition: all 0.3s ease;
        }
        textarea:focus {
            outline: none;
            border-color: #00e0ff;
            box-shadow: 0 0 0 3px rgba(0, 224, 255, 0.1);
        }
        button { 
            padding: 1rem 2.5rem; 
            margin-top: 1rem; 
            background: linear-gradient(135deg, #00e0ff, #00ff88); 
            color: #1a1a1a; 
            border: none; 
            border-radius: 12px; 
            cursor: pointer; 
            font-size: 1.1rem; 
            font-weight: 700;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        button:hover:not(:disabled) { 
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(0, 224, 255, 0.3);
        }
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        pre { 
            white-space: pre-wrap; 
            background: rgba(0, 0, 0, 0.3); 
            padding: 2rem; 
            border-radius: 12px; 
            border: 1px solid rgba(255, 255, 255, 0.1); 
            margin-top: 2rem;
            font-size: 0.95rem;
            line-height: 1.7;
            min-height: 100px;
            font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', monospace;
        }
        .loading {
            display: inline-block;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }
        .metric {
            background: rgba(255, 255, 255, 0.05);
            padding: 0.8rem;
            border-radius: 8px;
            text-align: center;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Jarvis Local Assistant</h1>
        <div id="status" class="status">🔄 Initializing system...</div>
        
        <div class="input-section">
            <label for="prompt">💬 Ask Jarvis anything:</label>
            <textarea id="prompt" placeholder="Type your question here... (Press Enter to send, Shift+Enter for new line)"></textarea>
        </div>
        
        <button onclick="sendChat()" id="sendBtn">🚀 Send Message</button>
        
        <pre id="output">Ready to chat with Jarvis! 💭</pre>
    </div>

    <script>
        let isProcessing = false;
        
        async function checkHealth() {
            try {
                const response = await fetch('/health');
                const data = await response.json();
                const statusEl = document.getElementById('status');
                
                if (response.ok) {
                    statusEl.textContent = `✅ System ${data.status} | Models: ${data.available_models.join(', ')}`;
                    statusEl.className = `status ${data.status}`;
                } else {
                    throw new Error('Health check failed');
                }
            } catch (error) {
                const statusEl = document.getElementById('status');
                statusEl.textContent = '❌ Error connecting to server';
                statusEl.className = 'status error';
            }
        }
        
        async function sendChat() {
            if (isProcessing) return;
            
            const prompt = document.getElementById('prompt').value.trim();
            if (!prompt) return;
            
            isProcessing = true;
            const output = document.getElementById('output');
            const button = document.getElementById('sendBtn');
            const textarea = document.getElementById('prompt');
            
            // UI updates
            output.innerHTML = '<span class="loading">🤔</span> Jarvis is thinking...';
            button.innerHTML = '<span class="loading">⏳</span> Processing...';
            button.disabled = true;
            textarea.disabled = true;
            
            try {
                const response = await fetch('/api/v1/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        persona: 'generalist',
                        messages: [{ role: 'user', content: prompt }],
                        temperature: 0.7,
                        max_tokens: 512
                    })
                });
                
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || `HTTP ${response.status}`);
                }
                
                const data = await response.json();
                
                // Display response with metrics
                const metricsHtml = `
                    <div class="metrics">
                        <div class="metric">📊 Tokens: ${data.tokens}</div>
                        <div class="metric">🤖 Model: ${data.model}</div>
                        <div class="metric">⚡ Status: Success</div>
                    </div>
                `;
                
                output.innerHTML = data.content + metricsHtml;
                
            } catch (error) {
                output.innerHTML = `❌ Error: ${error.message}`;
            } finally {
                isProcessing = false;
                button.innerHTML = '🚀 Send Message';
                button.disabled = false;
                textarea.disabled = false;
                textarea.focus();
            }
        }
        
        // Handle Enter key
        document.getElementById('prompt').addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendChat();
            }
        });
        
        // Initialize
        checkHealth();
        setInterval(checkHealth, 30000); // Check every 30 seconds
        
        // Focus textarea on load
        document.getElementById('prompt').focus();
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    run_server()
