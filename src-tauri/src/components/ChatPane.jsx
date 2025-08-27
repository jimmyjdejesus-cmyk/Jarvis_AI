import React, { useState, useEffect, useRef, useCallback } from 'react';
import { socket } from '../socket';
import API_CONFIG, { getApiUrl } from '../config';

// Chat customization settings with defaults
const DEFAULT_SETTINGS = {
  fontSize: 14,
  theme: 'dark',
  messageLimit: 100,
  autoScroll: true,
  showTimestamps: true,
  soundEnabled: true,
  compactMode: false,
  chatMode: 'chat', // 'chat', 'research', 'agent'
  neo4jUri: '',
  neo4jUser: '',
  neo4jPassword: '',
};

// Load settings from localStorage, excluding sensitive Neo4j credentials
const loadSettings = () => {
  try {
    const saved = localStorage.getItem('jarvis-chat-settings');
    if (!saved) return DEFAULT_SETTINGS;
    const parsed = JSON.parse(saved);
    delete parsed.neo4jUri;
    delete parsed.neo4jUser;
    delete parsed.neo4jPassword;
    return { ...DEFAULT_SETTINGS, ...parsed };
  } catch (e) {
    console.error('Failed to load chat settings:', e);
    return DEFAULT_SETTINGS;
  }
};

// Save settings to localStorage without Neo4j credentials
const saveSettings = (settings) => {
  try {
    const { neo4jUri, neo4jUser, neo4jPassword, ...toStore } = settings;
    localStorage.setItem('jarvis-chat-settings', JSON.stringify(toStore));
  } catch (e) {
    console.error('Failed to save chat settings:', e);
  }
};

const ChatPane = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [settings, setSettings] = useState(loadSettings);
  const [showSettings, setShowSettings] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId] = useState('default-session');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Apply settings to the chat pane
  const applySettings = useCallback((newSettings) => {
    setSettings(newSettings);
    saveSettings(newSettings);
    
    // Apply CSS custom properties for dynamic styling
    const chatPane = document.querySelector('.chat-pane');
    if (chatPane) {
      chatPane.style.setProperty('--chat-font-size', `${newSettings.fontSize}px`);
      chatPane.classList.toggle('theme-light', newSettings.theme === 'light');
      chatPane.classList.toggle('theme-dark', newSettings.theme === 'dark');
      chatPane.classList.toggle('compact-mode', newSettings.compactMode);
    }
  }, []);

  // Initialize settings on mount
  useEffect(() => {
    applySettings(settings);
  }, [settings, applySettings]);

  // WebSocket connection management
  useEffect(() => {
    const onConnect = () => {
      setIsConnected(true);
      const systemMessage = {
        id: Date.now(),
        type: 'system',
        text: `Connected to J.A.R.V.I.S. backend in ${settings.chatMode} mode.`,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, systemMessage]);
    };

    const onDisconnect = () => {
      setIsConnected(false);
      const systemMessage = {
        id: Date.now(),
        type: 'system',
        text: 'Disconnected from J.A.R.V.I.S. backend.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, systemMessage]);
    };

    const onChatResponse = (response) => {
      setIsTyping(false);
      const responseMessage = {
        id: Date.now(),
        type: 'response',
        text: response.data || response.message || 'No response',
        timestamp: new Date().toISOString(),
        mode: settings.chatMode
      };
      
      setMessages(prev => {
        const newMessages = [...prev, responseMessage];
        // Limit messages based on settings
        return newMessages.slice(-settings.messageLimit);
      });

      // Play notification sound if enabled
      if (settings.soundEnabled) {
        try {
          // Simple beep sound using Web Audio API
          const audioContext = new (window.AudioContext || window.webkitAudioContext)();
          const oscillator = audioContext.createOscillator();
          const gainNode = audioContext.createGain();
          
          oscillator.connect(gainNode);
          gainNode.connect(audioContext.destination);
          
          oscillator.frequency.value = 800;
          oscillator.type = 'sine';
          gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
          gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
          
          oscillator.start(audioContext.currentTime);
          oscillator.stop(audioContext.currentTime + 0.1);
        } catch (e) {
          console.log('Audio notification not available');
        }
      }
    };

    const onError = (error) => {
      setIsTyping(false);
      const errorMessage = {
        id: Date.now(),
        type: 'error',
        text: `Error: ${error.message || 'Unknown error occurred'}`,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    };

    // Register event listeners
    socket.on('connect', onConnect);
    socket.on('disconnect', onDisconnect);
    socket.on('chat_response', onChatResponse);
    socket.on('error', onError);

    // Check initial connection status
    if (socket.connected) {
      setIsConnected(true);
    }

    return () => {
      socket.off('connect', onConnect);
      socket.off('disconnect', onDisconnect);
      socket.off('chat_response', onChatResponse);
      socket.off('error', onError);
    };
  }, [settings.chatMode, settings.messageLimit, settings.soundEnabled]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (settings.autoScroll && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, settings.autoScroll]);

  // Handle message sending
  const handleSendMessage = useCallback((e) => {
    e.preventDefault();
    if (!input.trim() || !isConnected) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      text: input.trim(),
      timestamp: new Date().toISOString(),
      mode: settings.chatMode
    };

    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);

    // Send message with context about chat mode and trigger Cerebro
    socket.emit('chat_message', {
      message: input.trim(),
      mode: settings.chatMode,
      session_id: sessionId,
      timestamp: userMessage.timestamp,
      trigger_cerebro: true // This tells the galaxy to activate Cerebro
    });

    // Also send directly to galaxy visualization for immediate feedback
    socket.emit('cerebro_input', {
      message: input.trim(),
      timestamp: userMessage.timestamp,
      mode: settings.chatMode
    });

    setInput('');
    inputRef.current?.focus();
  }, [input, isConnected, settings.chatMode, sessionId]);

  // Send Neo4j credentials to backend
  const sendNeo4jConfig = useCallback(async (uri, user, password) => {
    try {
      await fetch(getApiUrl(API_CONFIG.ENDPOINTS.NEO4J_CONFIG), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': localStorage.getItem('jarvis-api-key') || '',
        },
        body: JSON.stringify({ uri, user, password }),
      });
    } catch (e) {
      console.error('Failed to update Neo4j configuration:', e);
    }
  }, []);

  // Handle settings change
  const handleSettingsChange = useCallback((key, value) => {
    const newSettings = { ...settings, [key]: value };
    applySettings(newSettings);

    if (['neo4jUri', 'neo4jUser', 'neo4jPassword'].includes(key)) {
      const { neo4jUri, neo4jUser, neo4jPassword } = newSettings;
      if (neo4jUri && neo4jUser && neo4jPassword) {
        sendNeo4jConfig(neo4jUri, neo4jUser, neo4jPassword);
      }
    }
  }, [settings, applySettings, sendNeo4jConfig]);

  // Clear chat messages
  const handleClearChat = useCallback(() => {
    if (window.confirm('Are you sure you want to clear all messages?')) {
      setMessages([]);
    }
  }, []);

  // Export chat history
  const handleExportChat = useCallback(() => {
    const chatData = {
      session_id: sessionId,
      exported_at: new Date().toISOString(),
      settings: settings,
      messages: messages
    };
    
    const blob = new Blob([JSON.stringify(chatData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `jarvis-chat-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [sessionId, settings, messages]);

  // Format timestamp for display
  const formatTimestamp = (timestamp) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString();
    } catch (e) {
      return '';
    }
  };

  // Get chat mode icon
  const getChatModeIcon = (mode) => {
    switch (mode) {
      case 'research': return '🔍';
      case 'agent': return '🤖';
      default: return '💬';
    }
  };

  return (
    <div className={`pane chat-pane theme-${settings.theme} ${settings.compactMode ? 'compact' : ''}`}>
      <div className="pane-header">
        <h2>
          {getChatModeIcon(settings.chatMode)} Chat
          <span className="chat-mode-badge">{settings.chatMode}</span>
        </h2>
        <div className="chat-controls">
          <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
            <span className="status-indicator"></span>
            {isConnected ? 'Connected' : 'Disconnected'}
          </div>
          <button 
            onClick={() => setShowSettings(!showSettings)} 
            className="btn-settings"
            title="Chat Settings"
          >
            ⚙️
          </button>
          <button 
            onClick={handleClearChat} 
            className="btn-clear"
            title="Clear Chat"
          >
            🗑️
          </button>
          <button 
            onClick={handleExportChat} 
            className="btn-export"
            title="Export Chat"
          >
            📤
          </button>
        </div>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <div className="settings-panel">
          <div className="settings-section">
            <label>
              Chat Mode:
              <select 
                value={settings.chatMode} 
                onChange={(e) => handleSettingsChange('chatMode', e.target.value)}
              >
                <option value="chat">💬 Chat</option>
                <option value="research">🔍 Research</option>
                <option value="agent">🤖 Agent</option>
              </select>
            </label>
          </div>

          <div className="settings-section">
            <label>
              Theme:
              <select 
                value={settings.theme} 
                onChange={(e) => handleSettingsChange('theme', e.target.value)}
              >
                <option value="dark">🌙 Dark</option>
                <option value="light">☀️ Light</option>
              </select>
            </label>
          </div>

          <div className="settings-section">
            <label>
              Font Size: {settings.fontSize}px
              <input
                type="range"
                min="10"
                max="24"
                value={settings.fontSize}
                onChange={(e) => handleSettingsChange('fontSize', parseInt(e.target.value))}
              />
            </label>
          </div>

          <div className="settings-section">
            <label>
              Message Limit:
              <input
                type="number"
                min="10"
                max="1000"
                value={settings.messageLimit}
                onChange={(e) => handleSettingsChange('messageLimit', parseInt(e.target.value))}
              />
            </label>
          </div>

          <div className="settings-section">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={settings.autoScroll}
                onChange={(e) => handleSettingsChange('autoScroll', e.target.checked)}
              />
              Auto-scroll to new messages
            </label>
          </div>

          <div className="settings-section">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={settings.showTimestamps}
                onChange={(e) => handleSettingsChange('showTimestamps', e.target.checked)}
              />
              Show timestamps
            </label>
          </div>

          <div className="settings-section">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={settings.soundEnabled}
                onChange={(e) => handleSettingsChange('soundEnabled', e.target.checked)}
              />
              Sound notifications
            </label>
          </div>

          <div className="settings-section">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={settings.compactMode}
                onChange={(e) => handleSettingsChange('compactMode', e.target.checked)}
              />
              Compact mode
            </label>
          </div>

          <div className="settings-section">
            <label>
              Neo4j URI:
              <input
                type="text"
                value={settings.neo4jUri}
                onChange={(e) => handleSettingsChange('neo4jUri', e.target.value)}
              />
            </label>
          </div>

          <div className="settings-section">
            <label>
              Neo4j User:
              <input
                type="text"
                value={settings.neo4jUser}
                onChange={(e) => handleSettingsChange('neo4jUser', e.target.value)}
              />
            </label>
          </div>

          <div className="settings-section">
            <label>
              Neo4j Password:
              <input
                type="password"
                value={settings.neo4jPassword}
                onChange={(e) => handleSettingsChange('neo4jPassword', e.target.value)}
              />
            </label>
          </div>
        </div>
      )}

      <div className="pane-content chat-messages" style={{ fontSize: `${settings.fontSize}px` }}>
        <div className="messages-container">
          {messages.map((msg) => (
            <div key={msg.id} className={`message ${msg.type}`}>
              <div className="message-content">
                <div className="message-header">
                  <strong className="message-sender">
                    {msg.type === 'user' ? 'You' : 
                     msg.type === 'system' ? 'System' :
                     msg.type === 'error' ? 'Error' : 'J.A.R.V.I.S.'}
                  </strong>
                  {settings.showTimestamps && msg.timestamp && (
                    <span className="message-timestamp">
                      {formatTimestamp(msg.timestamp)}
                    </span>
                  )}
                  {msg.mode && msg.mode !== 'chat' && (
                    <span className="message-mode">
                      {getChatModeIcon(msg.mode)} {msg.mode}
                    </span>
                  )}
                </div>
                <div className="message-text">{msg.text}</div>
              </div>
            </div>
          ))}
          
          {isTyping && (
            <div className="message response typing">
              <div className="message-content">
                <div className="message-header">
                  <strong className="message-sender">J.A.R.V.I.S.</strong>
                </div>
                <div className="message-text">
                  <span className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </span>
                  Thinking...
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      <form onSubmit={handleSendMessage} className="chat-input">
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={`Type your ${settings.chatMode} message...`}
          disabled={!isConnected}
          maxLength={1000}
        />
        <button 
          type="submit" 
          disabled={!isConnected || !input.trim()}
          className="btn-send"
        >
          {isConnected ? '📤' : '⏸️'} Send
        </button>
      </form>

      {!isConnected && (
        <div className="connection-warning">
          ⚠️ Not connected to backend. Please check your connection.
        </div>
      )}
    </div>
  );
};

export default ChatPane;
