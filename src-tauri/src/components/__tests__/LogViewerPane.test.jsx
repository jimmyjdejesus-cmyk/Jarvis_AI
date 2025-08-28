import React from 'react';
import { render, screen, act, waitFor, fireEvent } from '@testing-library/react';
import LogViewerPane from '../LogViewerPane';
import { socket } from '../../socket';
import { http } from '@tauri-apps/api';

jest.mock('@tauri-apps/api', () => ({
  http: { fetch: jest.fn() },
}));

test('shows connection status and HITL badge', async () => {
  http.fetch.mockResolvedValue({ ok: true, data: 'first line' });

  render(<LogViewerPane />);
  await screen.findByText(/first line/);

  expect(
    screen.getByTitle('Disconnected from real-time updates')
  ).toHaveClass('disconnected');

  await act(async () => {
    socket.emit('connect');
  });
  await waitFor(() =>
    expect(
      screen.getByTitle('Connected to real-time updates')
    ).toHaveClass('connected')
  );

  await act(async () => {
    socket.emit('disconnect');
  });
  await waitFor(() =>
    expect(
      screen.getByTitle('Disconnected from real-time updates')
    ).toHaveClass('disconnected')
  );
});

test('displays error and retries fetch successfully', async () => {
  http.fetch
    .mockRejectedValueOnce(new Error('network'))
    .mockResolvedValueOnce({ ok: true, data: 'first line' });

  render(<LogViewerPane />);

  await screen.findByText(/Failed to load agent logs/);

  fireEvent.click(screen.getByRole('button', { name: /try again/i }));

  await screen.findByText(/first line/);
  expect(screen.queryByText(/Failed to load agent logs/)).not.toBeInTheDocument();
});
