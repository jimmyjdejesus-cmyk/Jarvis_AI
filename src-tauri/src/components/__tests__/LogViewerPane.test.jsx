import { render, screen, act, waitFor } from '@testing-library/react';
import LogViewerPane from '../LogViewerPane';
import { socket } from '../../socket';

jest.mock('../../socket', () => {
  const handlers = {};
  return {
    socket: {
      emit: jest.fn((event) => {
        if (handlers[event]) {
          handlers[event]();
        }
      }),
      on: jest.fn((event, handler) => {
        handlers[event] = handler;
      }),
      off: jest.fn((event) => {
        delete handlers[event];
      }),
      connected: false,
    },
  };
});

jest.mock('@tauri-apps/api', () => ({
  http: {
    fetch: jest.fn().mockResolvedValue({ ok: true, data: 'first line', status: 200 }),
  },
}));

test('shows connection status and HITL badge', async () => {
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


