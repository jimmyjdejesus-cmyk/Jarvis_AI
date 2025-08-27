import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import LogViewerPane from '../LogViewerPane';
import { socket } from '../../socket';
import { http } from '@tauri-apps/api';

jest.mock('../../socket', () => {
  const handlers = {};
  return {
    socket: {
      on: (event, cb) => {
        handlers[event] = cb;
      },
      off: (event) => {
        delete handlers[event];
      },
      emit: (event, data) => {
        if (handlers[event]) {
          handlers[event](data);
        }
      },
      _handlers: handlers,
    },
  };
});

jest.mock('@tauri-apps/api', () => ({
  http: {
    fetch: jest.fn(),
    ResponseType: { Text: 'Text' },
  },
}));

describe('LogViewerPane', () => {
  beforeEach(() => {
    http.fetch.mockResolvedValue({ ok: true, data: 'first line\nsecond line' });
  });

  test('filters log lines based on input', async () => {
    render(<LogViewerPane />);
    await screen.findByText(/first line/);

    const input = screen.getByPlaceholderText('Filter logs...');
    fireEvent.change(input, { target: { value: 'second' } });

    expect(screen.queryByText(/first line/)).not.toBeInTheDocument();
    expect(screen.getByText(/second line/)).toBeInTheDocument();
  });

  test('shows connection status and HITL badge', async () => {
    render(<LogViewerPane />);
    await screen.findByText(/first line/);

    expect(screen.getByTitle('Disconnected from real-time updates')).toHaveClass('disconnected');

    await act(async () => {
      socket.emit('connect');
    });
    await waitFor(() =>
      expect(screen.getByTitle('Connected to real-time updates')).toHaveClass('connected')
    );

    await act(async () => {
      socket.emit('disconnect');
    });
    await waitFor(() =>
      expect(screen.getByTitle('Disconnected from real-time updates')).toHaveClass('disconnected')
    );

    await act(async () => {
      socket.emit('hitl_update', ['a', 'b']);
    });
    expect(await screen.findByText('2')).toHaveClass('hitl-badge');

    await act(async () => {
      socket.emit('hitl_update', []);
    });
    await waitFor(() =>
      expect(screen.queryByText('2')).not.toBeInTheDocument()
    );
  });
});
