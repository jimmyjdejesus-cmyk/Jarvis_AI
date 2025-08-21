import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import Dict, Any
import time

from jarvis.dynamic_agents import create_dynamic_agent, default_tools
from jarvis.persistence.session import SessionManager

NODE_STYLE = {
    "planning": {"fill": "#dfefff"},
    "research": {"fill": "#e8ffe8"},
    "analysis": {"fill": "#ffeedd"},
    "error": {"fill": "#ffd6d6"},
}

class JarvisChatUI:
    def __init__(self, master: tk.Tk | None = None) -> None:
        self.master = master or tk.Tk()
        self.master.title("Jarvis AI – Local Assistant")
        self.master.geometry("1000x650")
        self.master.minsize(900, 550)

        self.sessions = SessionManager()
        self.session_id = self.sessions.create()

        # Menu
        menubar = tk.Menu(self.master)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Session", command=self.new_session)
        file_menu.add_command(label="Load Session…", command=self.load_session_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self.master.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        self.master.config(menu=menubar)

        # Paned layout
        paned = ttk.PanedWindow(self.master, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Left: chat + history
        left = ttk.Frame(paned)
        paned.add(left, weight=3)

        # Right: workflow canvas + inspector
        right = ttk.Frame(paned)
        paned.add(right, weight=2)

        # Left top: chat history
        left.rowconfigure(0, weight=1)
        left.columnconfigure(0, weight=1)
        self.history = scrolledtext.ScrolledText(left, wrap=tk.WORD, state=tk.DISABLED)
        self.history.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=6, pady=6)

        # Left bottom: prompt + buttons
        self.prompt = tk.Entry(left)
        self.prompt.grid(row=1, column=0, sticky="we", padx=6, pady=(0,6))
        self.prompt.bind("<Return>", lambda e: self.run_agent())

        btn = ttk.Button(left, text="Run", command=self.run_agent)
        btn.grid(row=1, column=1, sticky="e", padx=6, pady=(0,6))

        # Right split: Canvas (graph) on top, step inspector below
        right.rowconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        # Graph canvas
        self.canvas = tk.Canvas(right, bg="#fafafa", highlightthickness=1, highlightbackground="#ddd")
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=6, pady=(6,3))

        # Step inspector
        self.step_view = scrolledtext.ScrolledText(right, wrap=tk.WORD, state=tk.DISABLED, height=10)
        self.step_view.grid(row=1, column=0, sticky="nsew", padx=6, pady=(3,6))

        # Build default agent
        self.agent = create_dynamic_agent(
            "gui_agent",
            {
                "planning": default_tools.planning_tool,
                "research": default_tools.research_tool,
                "analysis": default_tools.analysis_tool,
            },
        )

        # Keep node refs for clicks
        self.node_positions = {}
        self._write_history(f"Session created: {self.session_id}")


    def _write_history(self, text: str) -> None:
        self.history.configure(state=tk.NORMAL)
        self.history.insert(tk.END, text + "\n")
        self.history.configure(state=tk.DISABLED)
        self.history.see(tk.END)

    def _write_step(self, title: str, content: str) -> None:
        self.step_view.configure(state=tk.NORMAL)
        self.step_view.delete("1.0", tk.END)
        self.step_view.insert(tk.END, f"{title}\n\n{content}")
        self.step_view.configure(state=tk.DISABLED)

    # Session management
    def new_session(self) -> None:
        self.session_id = self.sessions.create()
        self._write_history("")  # spacing
        self._write_history(f"New session: {self.session_id}")

    def load_session_dialog(self) -> None:
        sessions = self.sessions.list_sessions()
        if not sessions:
            messagebox.showinfo("No sessions", "No saved sessions found yet.")
            return
        # Simple chooser in a new window
        win = tk.Toplevel(self.master)
        win.title("Load Session")
        lb = tk.Listbox(win, width=50, height=10)
        for meta in sessions:
            lb.insert(tk.END, f"{meta['id']}  —  {meta['name']}  (runs: {meta.get('runs',0)})")
        lb.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        def choose():
            idx = lb.curselection()
            if not idx:
                return
            chosen = sessions[idx[0]]["id"]
            self.session_id = chosen
            self._write_history("")  # spacing
            self._write_history(f"Loaded session: {self.session_id}")
            win.destroy()

        ttk.Button(win, text="Load", command=choose).pack(pady=(0,8))

    # Drawing workflow graph
    def _draw_workflow(self, results: Dict[str, Any]) -> None:
        self.canvas.delete("all")
        w = self.canvas.winfo_width() or 600
        h = self.canvas.winfo_height() or 300

        nodes = list(results.keys())
        if not nodes:
            return
        pad = 30
        node_w, node_h = 160, 60
        gap = (w - 2*pad - node_w) // max(1, (len(nodes)-1))

        self.node_positions.clear()
        last_center = None
        for i, name in enumerate(nodes):
            x = pad + node_w//2 + i * gap
            y = h//2
            style = NODE_STYLE.get(name, {"fill": "#eef"})
            rect = self.canvas.create_rectangle(x-node_w//2, y-node_h//2,
                                                x+node_w//2, y+node_h//2,
                                                fill=style.get("fill","#eef"), outline="#889" )
            text = self.canvas.create_text(x, y, text=name.capitalize(), font=("TkDefaultFont", 11, "bold"))
            self.node_positions[rect] = name
            self.node_positions[text] = name
            if last_center is not None:
                self.canvas.create_line(last_center[0]+node_w//2, last_center[1],
                                        x-node_w//2, y, arrow=tk.LAST, fill="#777", width=2)
            last_center = (x, y)

        # bind clicks
        self.canvas.tag_bind("all", "<Button-1>", self._on_canvas_click)

    def _on_canvas_click(self, event):
        # find nearest item, show its content
        item = self.canvas.find_closest(event.x, event.y)
        name = self.node_positions.get(item[0])
        if not name:
            return
        content = self.last_results.get(name, "(no content)")
        if isinstance(content, dict):
            content = str(content)
        self._write_step(f"{name.capitalize()}", content)

    # Running the agent
    def run_agent(self) -> None:
        objective = self.prompt.get().strip()
        if not objective:
            return
        self.prompt.delete(0, tk.END)
        self._write_history(f"You: {objective}")

        # Execute steps and stream to UI
        results: Dict[str, Any] = {}
        steps = [("planning", default_tools.planning_tool),
                 ("research", default_tools.research_tool),
                 ("analysis", default_tools.analysis_tool)]

        for name, func in steps:
            # Draw progressive graph with known nodes
            tmp_results = results.copy()
            tmp_results[name] = "(running…)"
            self._draw_workflow(tmp_results)
            self.master.update_idletasks()
            time.sleep(0.05)  # tiny delay for UX

            try:
                out = func(objective, results)
            except Exception as e:
                out = {"error": str(e)}
            results[name] = out

            # update inspector to current step
            pretty = out if isinstance(out, str) else str(out)
            self._write_step(name.capitalize(), pretty)
            self.master.update_idletasks()

        self.last_results = results
        self._draw_workflow(results)

        # Append to history area
        for step, out in results.items():
            self._write_history(f"— {step.capitalize()} completed.")
        self._write_history("(Click nodes on the right to inspect details.)\n" )

        # Persist run
        record = {"objective": objective, "results": results, "ts": int(time.time())}
        self.sessions.append_run(self.session_id, record)


def main() -> None:
    ui = JarvisChatUI()
    ui.start()

if __name__ == "__main__":
    main()
