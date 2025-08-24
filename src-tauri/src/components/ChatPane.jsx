import React, { useState, useEffect, useRef } from 'react';
import { socket } from '../socket'; // We will create this file next

// DEV-COMMENT: The ChatPane is the primary user interaction component.
// It manages the state for messages and user input, and it communicates
// with the backend over WebSockets for real-time chat.

const ChatPane = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  // DEV-COMMENT: The useEffect hook is used to manage the WebSocket connection's lifecycle.
  // We establish listeners when the component mounts and clean them up when it unmounts.
  useEffect(() => {
    // Function to handle incoming chat responses from the server
    const onChatResponse = (response) => {
      setMessages(prev => [...prev, { type: 'response', text: response.data }]);
    };

    // Function to handle connection confirmation
    const onConnect = () => {
        setMessages(prev => [...prev, { type: 'system', text: 'Connected to J.A.R.V.I.S. backend.' }]);
    };

    socket.on('connect', onConnect);
    socket.on('chat_response', onChatResponse);

    // DEV-COMMENT: The cleanup function returned by useEffect is crucial for preventing memory leaks.
    // It removes the event listeners when the component is no longer in use.
    return () => {
      socket.off('connect', onConnect);
      socket.off('chat_response', onChatResponse);
    };
  }, []);

  // DEV-COMMENT: This useEffect hook ensures that the chat window automatically
  // scrolls to the latest message whenever new messages are added.
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (input.trim()) {
      const userMessage = { type: 'user', text: input };
      setMessages(prev => [...prev, userMessage]);
      // DEV-COMMENT: We emit a 'chat_message' event to the backend with the user's input.
      // The backend will process this and send a 'chat_response' back.
      socket.emit('chat_message', { message: input });
      setInput('');
    }
  };

  return (
    <div className="pane">
      <h2>Chat</h2>
      <div className="pane-content chat-messages">
        <div>
          {messages.map((msg, index) => (
            <p key={index} className={`message ${msg.type}`}>
              <strong>{msg.type === 'user' ? 'You' : 'J.A.R.V.I.S.'}:</strong> {msg.text}
            </p>
          ))}
          <div ref={messagesEndRef} />
        </div>
      </div>
      <form onSubmit={handleSendMessage} className="chat-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
};

export default ChatPane;
