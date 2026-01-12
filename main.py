import tkinter as tk
from tkinter import ttk
from src.interface import App
from src.paths import JSON_PATH
from src import loggers
import logging

LOG = logging.getLogger(__name__)

def main():
    loggers.setup_basic_logging()
    window = tk.Tk()
    window.geometry('750x750')
    window.title('Flags')

    style = ttk.Style()
    style.configure('Treeview',rowheight=35)

    myapp = App(window,750,800,JSON_PATH)
    myapp.mainloop()


if __name__ == "__main__":
    main()
