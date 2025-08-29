import React, { useEffect, useRef, useState, useCallback } from 'react';
import { socket } from '../socket';
import API_CONFIG, { getApiUrl } from '../config';
import './formStyles.css';

const ChatPane = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [connected, setConnected] = useState(false);
  const [sending, setSending] = useState(false);
  const containerRef = useRef(null);

  // Auto-scroll to bottom on message add
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [messages]);

  // WebSocket status + handlers
  useEffect(() => {
    const onConnect = () => setConnected(true);
    const onDisconnect = () => setConnected(false);
    const onChatResponse = (data) => {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', text: data?.message || JSON.stringify(data), at: new Date().toISOString() },
      ]);
    };
    const onThinking = (data) => {
      setMessages((prev) => [
        ...prev,
        { role: 'system', text: data?.status || 'Thinking…', at: new Date().toISOString() },
      ]);
    };

    socket.on('connect', onConnect);
    socket.on('disconnect', onDisconnect);
    socket.on('chat_response', onChatResponse);
    socket.on('cerebro_response', onChatResponse);
    socket.on('cerebro_thinking', onThinking);

    setConnected(socket.connected);
    return () => {
      socket.off('connect', onConnect);
      socket.off('disconnect', onDisconnect);
      socket.off('chat_response', onChatResponse);
      socket.off('cerebro_response', onChatResponse);
      socket.off('cerebro_thinking', onThinking);
    };
  }, []);

  const sendViaBackend = useCallback(async (text) => {
    // Prefer WebSocket if available; fallback to knowledge query
    if (socket && socket.connected) {
      socket.emit('chat_message', { message: text });
      return true;
    }
    try {
      const url = getApiUrl(`/knowledge/query?q=${encodeURIComponent(text)}`);
      const resp = await fetch(url);
      if (resp.ok) {
        const data = await resp.json();
        setMessages((prev) => [
          ...prev,
          { role: 'assistant', text: JSON.stringify(data.results ?? data), at: new Date().toISOString() },
        ]);
        return true;
      }
    } catch (e) {
      // ignore, handled below
    }
    setMessages((prev) => [
      ...prev,
      { role: 'error', text: 'Backend not connected. Showing local echo.', at: new Date().toISOString() },
    ]);
    return false;
  }, []);

  const send = async () => {
    const text = input.trim();
    if (!text) return;
    setSending(true);
    setMessages((prev) => [...prev, { role: 'user', text, at: new Date().toISOString() }]);
    setInput('');
    try {
      await sendViaBackend(text);
    } finally {
      setSending(false);
    }
  };

  const onKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  return (
    <div className="pane chat-pane">
      {!connected && (
        <div className="connection-warning">Backend WebSocket disconnected. Falling back to HTTP.</div>
      )}

      <div className="chat-messages">
        <div className="messages-container" ref={containerRef}>
          {messages.map((m, i) => (
            <div key={i} className={`message ${m.role}`}>
              <div className="message-header">
                <span className="message-sender">{m.role}</span>
                <span className="message-timestamp">{new Date(m.at).toLocaleTimeString()}</span>
              </div>
              <div className="message-content">
                <div className="message-text">{m.text}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="chat-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder={connected ? 'Message Cerebro…' : 'Type a question (HTTP fallback)…'}
          disabled={sending}
        />
        <button className="btn-send" onClick={send} disabled={sending || !input.trim()}>
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatPane;
