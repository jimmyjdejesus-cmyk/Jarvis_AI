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