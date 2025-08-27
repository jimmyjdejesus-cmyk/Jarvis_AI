import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import LoginForm from '../LoginForm';
import { setAuthToken } from '../../auth';
import { getApiUrl } from '../../config';

jest.mock('../../auth', () => ({
  setAuthToken: jest.fn(),
}));

jest.mock('../../config', () => ({
  getApiUrl: jest.fn(() => '/token'),
}));

describe('LoginForm', () => {
  beforeEach(() => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ access_token: 'abc123' }),
    });
  });

  test('logs in and stores token', async () => {
    const onLogin = jest.fn();
    render(<LoginForm onLogin={onLogin} />);

    fireEvent.change(screen.getByPlaceholderText('Username'), { target: { value: 'user' } });
    fireEvent.change(screen.getByPlaceholderText('Password'), { target: { value: 'pass' } });
    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => expect(setAuthToken).toHaveBeenCalledWith('abc123'));
    expect(onLogin).toHaveBeenCalled();
    expect(global.fetch).toHaveBeenCalled();
  });
});
