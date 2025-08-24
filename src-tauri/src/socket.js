import { io } from 'socket.io-client';

// DEV-COMMENT: This module centralizes the Socket.IO client connection.
// By exporting a single instance of the socket, we ensure that the entire
// application shares the same connection to the backend, preventing multiple
// unnecessary connections from different components.

const URL = 'ws://127.0.0.1:8000';
// The path option is important to match the server-side mount point.
export const socket = io(URL, { path: "/ws/socket.io" });
