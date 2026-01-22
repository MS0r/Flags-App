import tkinter as tk
from tkinter import ttk
from flags.interface import App
from flags.paths import JSON_PATH, SQLITE_PATH
from flags.loggers import setup_logging

LOG = setup_logging(__name__)

def main():
    window = tk.Tk()
    window.geometry('750x750')
    window.title('Flags')

    style = ttk.Style()
    style.configure('Treeview',rowheight=35)

    myapp = App(window,750,800,SQLITE_PATH)
    myapp.mainloop()


if __name__ == "__main__":
    main()
