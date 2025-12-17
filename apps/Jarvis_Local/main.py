# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



# main.py
import tkinter as tk
from Jarvis_Local.ui.main_window.app import MainWindow
from logger_config import log

if __name__ == "__main__":
    log.info("Starting J.A.R.V.I.S. application...")
    root = tk.Tk()
    root.title("J.A.R.V.I.S. Control Console")
    main_app = MainWindow(root)
    main_app.pack(fill="both", expand=True)
    root.mainloop()
    log.info("J.A.R.V.I.S. application closed.")