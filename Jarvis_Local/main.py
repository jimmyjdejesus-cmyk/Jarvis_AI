# main.py
import tkinter as tk
from ui.main_window.app import MainWindow
from logger_config import log

if __name__ == "__main__":
    log.info("Starting J.A.R.V.I.S. application...")
    root = tk.Tk()
    root.title("J.A.R.V.I.S. Control Console")
    main_app = MainWindow(root)
    main_app.pack(fill="both", expand=True)
    root.mainloop()
    log.info("J.A.R.V.I.S. application closed.")