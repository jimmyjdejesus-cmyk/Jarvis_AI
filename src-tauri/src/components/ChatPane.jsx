import React, { useState, useEffect, useRef, useCallback } from 'react';
import { socket } from '../socket';

import Neo4jConfigForm from './Neo4jConfigForm';
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
};

// Load settings from localStorage, excluding sensitive Neo4j credentials
const loadSettings = () => {
  try {
    const saved = localStorage.getItem('jarvis-chat-settings');
    if (!saved) return DEFAULT_SETTINGS;
    const parsed = JSON.parse(saved);

    return { ...DEFAULT_SETTINGS, ...parsed };
  } catch (e) {
    console.error('Failed to load chat settings:', e);
    return DEFAULT_SETTINGS;
  }
};

// Save settings to localStorage without Neo4j credentials
const saveSettings = (settings) => {
// ... (the rest of the file continues) ...