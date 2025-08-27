// Enhanced WebSocket client for FastAPI backend integration
// Provides Socket.IO-like interface for compatibility with existing components

class EnhancedWebSocket {
  constructor(url) {
    this.url = url;
    this.ws = null;
    this.connected = false;
    this.eventHandlers = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
    this.clientId = `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    this.connect();
  }

  connect() {
    try {
      const apiKey = API_CONFIG.API_KEY ? `?api_key=${encodeURIComponent(API_CONFIG.API_KEY)}` : '';
      const wsUrl = `${this.url}/ws/${this.clientId}${apiKey}`;
      console.log('Connecting to WebSocket:', wsUrl);
      
      this.ws = new WebSocket(wsUrl);
      
      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.connected = true;
        this.reconnectAttempts = 0;
        this.emit('connect');
      };
      
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('WebSocket message received:', data);
          
          if (data.type) {
            this.emit(data.type, data.data || data);
          }
        } catch (e) {
          console.error('Error parsing WebSocket message:', e);
        }
      };
      
      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.connected = false;
        this.emit('disconnect');
        this.handleReconnect();
      };
      
      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.emit('error', error);
      };
      
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      this.handleReconnect();
    }
  }

  handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
      
      setTimeout(() => {
        this.connect();
      }, this.reconnectDelay * this.reconnectAttempts);
    } else {
      console.error('Max reconnection attempts reached');
    }
  }

  // Socket.IO-like interface for compatibility
  on(event, handler) {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, []);
    }
    this.eventHandlers.get(event).push(handler);
  }

  off(event, handler) {
    if (this.eventHandlers.has(event)) {
      const handlers = this.eventHandlers.get(event);
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  emit(event, data) {
    // If it's an outgoing event (to server)
    if (this.ws && this.ws.readyState === WebSocket.OPEN && typeof event === 'string' && data !== undefined) {
      const message = {
        type: event,
        data: data,
        timestamp: new Date().toISOString(),
        client_id: this.clientId
      };
      this.ws.send(JSON.stringify(message));
      return;
    }
    
    // If it's an incoming event (from server) or internal event
    if (this.eventHandlers.has(event)) {
      this.eventHandlers.get(event).forEach(handler => {
        try {
          handler(data);
        } catch (e) {
          console.error(`Error in event handler for ${event}:`, e);
        }
      });
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

import API_CONFIG, { getWebSocketUrl } from './config.js';

// Create and export the socket instance
const socket = new EnhancedWebSocket(getWebSocketUrl());

// Add some debugging
window.jarvisSocket = socket; // For debugging in browser console

// Add connection status logging
socket.on('connect', () => {
  console.log('✅ Cerebro Galaxy Backend Connected!');
});

socket.on('disconnect', () => {
  console.log('❌ Cerebro Galaxy Backend Disconnected');
});

socket.on('error', (error) => {
  console.error('🔥 WebSocket Connection Error:', error);
});

export { socket };
