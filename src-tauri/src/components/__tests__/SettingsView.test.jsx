import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import SettingsView from '../SettingsView';
import * as config from '../../config';

jest.spyOn(config, 'setBackendBaseUrl');
jest.spyOn(config, 'setApiKey');

  describe('SettingsView', () => {
    beforeEach(() => {
      localStorage.clear();
      config.setBackendBaseUrl.mockClear();
      config.setApiKey.mockClear();
    });

    test('updates backend URL and API key in localStorage', () => {
      render(<SettingsView />);

    const urlInput = screen.getByLabelText(/Backend URL/i);
    fireEvent.change(urlInput, { target: { value: 'http://example.com' } });
    expect(config.setBackendBaseUrl).toHaveBeenCalledWith('http://example.com');
    expect(localStorage.getItem('jarvis-backend-url')).toBe('http://example.com');

    const keyInput = screen.getByLabelText(/API Key/i);
    fireEvent.change(keyInput, { target: { value: 'secret' } });
    expect(config.setApiKey).toHaveBeenCalledWith('secret');
      expect(localStorage.getItem('jarvis-api-key')).toBe('secret');
    });

    test('saves Black team settings', () => {
      render(<SettingsView />);
      fireEvent.click(screen.getByRole('button', { name: /Teams/i }));
      const curiosity = screen.getByLabelText(/Curiosity/i);
      fireEvent.change(curiosity, { target: { value: '70' } });
      const stored = JSON.parse(localStorage.getItem('jarvis-team-settings'));
      expect(stored.Black.curiosity).toBe(70);
    });
  });
