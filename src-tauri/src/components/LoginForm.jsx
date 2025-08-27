import React, { useState } from 'react';
import { getApiUrl } from '../config';
import { setAuthToken } from '../auth';

/**
 * Simple login form that obtains a JWT from the backend and stores it via setAuthToken.
 */
const LoginForm = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      const res = await fetch(getApiUrl('/token'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ username, password })
      });
      if (!res.ok) {
        throw new Error('Login failed');
      }
      const data = await res.json();
      setAuthToken(data.access_token);
      if (onLogin) onLogin();
    } catch (err) {
      console.error('Login error:', err);
      setError('Invalid credentials');
    }
  };

  return (
    <form className="login-form" onSubmit={handleSubmit}>
      <h2>Login</h2>
      <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      {error && <p className="error-message">{error}</p>}
      <button type="submit">Login</button>
    </form>
  );
};

export default LoginForm;
