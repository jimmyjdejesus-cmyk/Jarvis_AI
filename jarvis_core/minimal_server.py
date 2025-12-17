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
Minimal Jarvis server that works without complex middleware.
"""

from __future__ import annotations

from typing import List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from jarvis_core.app import AdaptiveMindApplication
from jarvis_core.config import load_config

# Request/Response Models
class ChatRequest(BaseModel):
    messages: List[dict]
    persona: str = "generalist"
    temperature: float = 0.7
    max_tokens: int = 512

class ChatResponse(BaseModel):
    content: str
    model: str
    tokens: int
    diagnostics: dict = {}

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    config = load_config()
    jarvis_app = AdaptiveMindApplication(config=config)
    
    app = FastAPI(
        title="AdaptiveMind Local Assistant",
        version="1.0.0",
        description="Local-first AI assistant with persona routing"
    )
    
    @app.get("/")
    async def root():
        return HTMLResponse(content=_INDEX_HTML)
    
    @app.get("/health")
    async def health():
        models = jarvis_app.models()
        status_value = "ok" if models else "degraded"
        return {
            "status": status_value,
            "available_models": models
        }
    
    @app.post("/api/v1/chat")
    async def chat(request: ChatRequest):
        try:
            # Validate persona
            if request.persona not in jarvis_app.config.personas:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Persona '{request.persona}' not found. Available: {list(jarvis_app.config.personas.keys())}"
                )
            
            # Generate response
            payload = jarvis_app.chat(
                persona=request.persona,
                messages=request.messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
            
            return ChatResponse(**payload)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Chat request failed: {str(e)}"
            )
    
    return app

_INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>🤖 AdaptiveMind Local Assistant</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
            margin: 0; 
            padding: 2rem; 
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); 
            color: #f8f9fa; 
            min-height: 100vh; 
        }
        .container { 
            max-width: 800px; 
            margin: 0 auto; 
            background: rgba(255, 255, 255, 0.1); 
            padding: 2rem; 
            border-radius: 16px; 
            backdrop-filter: blur(10px); 
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
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
            font-weight: bold;
        }
        .status.ok { background: rgba(40, 167, 69, 0.2); border: 1px solid #28a745; }
        .status.degraded { background: rgba(255, 193, 7, 0.2); border: 1px solid #ffc107; }
        textarea { 
            width: 100%; 
            height: 120px; 
            padding: 1rem; 
            background: rgba(255, 255, 255, 0.1); 
            color: #f8f9fa; 
            border: 1px solid rgba(255, 255, 255, 0.2); 
            border-radius: 8px; 
            resize: vertical;
            font-size: 1rem;
        }
        button { 
            padding: 1rem 2rem; 
            margin-top: 1rem; 
            background: #00e0ff; 
            color: #1e3c72; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer; 
            font-size: 1rem; 
            font-weight: bold;
            transition: all 0.3s ease;
        }
        button:hover { 
            background: #00b8d4; 
            transform: translateY(-2px);
        }
        pre { 
            white-space: pre-wrap; 
            background: rgba(0, 0, 0, 0.3); 
            padding: 1.5rem; 
            border-radius: 8px; 
            border: 1px solid rgba(255, 255, 255, 0.1); 
            margin-top: 1.5rem;
            font-size: 0.9rem;
            line-height: 1.6;
        }
        label { 
            display: block; 
            margin-bottom: 0.5rem; 
            font-weight: bold; 
            color: #e9ecef;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 AdaptiveMind Local Assistant</h1>
        <div id="status" class="status">Checking system status...</div>
        
        <label for="prompt">Ask AdaptiveMind anything:</label>
        <textarea id="prompt" placeholder="Type your question here..."></textarea>
        
        <button onclick="sendChat()">🚀 Send Message</button>
        <pre id="output">Response will appear here.</pre>
    </div>

    <script>
        let isProcessing = false;
        
        async function checkHealth() {
            try {
                const response = await fetch('/health');
                const data = await response.json();
                const statusEl = document.getElementById('status');
                statusEl.textContent = `Status: ${data.status} | Models: ${data.available_models.join(', ')}`;
                statusEl.className = `status ${data.status}`;
            } catch (error) {
                const statusEl = document.getElementById('status');
                statusEl.textContent = '❌ Error connecting to server';
                statusEl.className = 'status degraded';
            }
        }
        
        async function sendChat() {
            if (isProcessing) return;
            
            const prompt = document.getElementById('prompt').value.trim();
            if (!prompt) return;
            
            isProcessing = true;
            const output = document.getElementById('output');
            const button = document.querySelector('button');
            
            // UI updates
            output.textContent = '🤔 AdaptiveMind is thinking...';
            button.textContent = '⏳ Processing...';
            button.disabled = true;
            
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
                    throw new Error(errorData.detail || `HTTP ${response.status}`);
                }
                
                const data = await response.json();
                output.textContent = data.content + '\\n\\n📊 Tokens: ' + data.tokens + ' | 🤖 Model: ' + data.model;
                
            } catch (error) {
                output.textContent = '❌ Error: ' + error.message;
            } finally {
                isProcessing = false;
                button.textContent = '🚀 Send Message';
                button.disabled = false;
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
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    import uvicorn
    app = create_app()
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
