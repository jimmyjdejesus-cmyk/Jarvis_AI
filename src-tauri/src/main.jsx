import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles.css';

// DEV-COMMENT: This is the standard entry point for a React application.
// It finds the 'root' DOM element (defined in index.html) and renders our main <App /> component into it.
// The StrictMode wrapper helps catch potential problems in the application during development.

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
