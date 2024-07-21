import tkinter as tk
from tkinter import ttk
from interface import App
from paths import (json_path)

#App initialization
window = tk.Tk()
window.geometry('750x750')
window.title('Flags')

style = ttk.Style()
style.configure('Treeview',rowheight=35)

myapp = App(window,750,800,json_path)
myapp.mainloop()
