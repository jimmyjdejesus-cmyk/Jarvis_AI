"""Tkinter-based chat UI for the local J.A.R.V.I.S. Meta-Agent."""

import tkinter as tk
from tkinter import scrolledtext, Entry, Button, Frame
from threading import Thread
from orchestrator import Orchestrator


class ChatApplication(Frame):
    """Simple Tkinter chat interface for interacting with the Meta-Agent."""

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("J.A.R.V.I.S. Local Console")
        self.pack(pady=10, padx=10)
        self.create_widgets()

        # Initialize the backend orchestrator
        self.orchestrator = Orchestrator()
        self.add_message("J.A.R.V.I.S.: Meta-Agent online. How can I help you?")

    def create_widgets(self):
        """Create chat log, entry box, and send button."""
        self.chat_log = scrolledtext.ScrolledText(self, state='disabled', height=25, width=80, wrap=tk.WORD)
        self.chat_log.pack()

        self.entry_box = Entry(self, width=80)
        self.entry_box.pack(pady=10)
        self.entry_box.bind("<Return>", self.send_message_event)

        self.send_button = Button(self, text="Send", command=self.send_message)
        self.send_button.pack()

    def send_message_event(self, event):
        """Handle Enter key press events to send messages."""
        self.send_message()

    def send_message(self):
        """Send user input to the orchestrator and display the response."""
        user_input = self.entry_box.get()
        if user_input:
            self.add_message(f"You: {user_input}")
            self.entry_box.delete(0, tk.END)

            # Disable input while the agent is thinking
            self.entry_box.config(state='disabled')
            self.send_button.config(state='disabled')

            # Run agent processing in a separate thread to keep UI responsive
            thread = Thread(target=self.get_agent_response, args=(user_input,))
            thread.start()

    def get_agent_response(self, user_input):
        """Fetch response from the orchestrator in a background thread."""
        response = self.orchestrator.handle_request(user_input)
        self.add_message(f"J.A.R.V.I.S.: {response}")

        # Re-enable input
        self.entry_box.config(state='normal')
        self.send_button.config(state='normal')

    def add_message(self, message):
        """Append a message to the chat log."""
        self.chat_log.config(state='normal')
        self.chat_log.insert(tk.END, message + "\n\n")
        self.chat_log.config(state='disabled')
        self.chat_log.yview(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApplication(master=root)
    app.mainloop()
