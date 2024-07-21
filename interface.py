import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from src.country import Countries

class App(tk.Frame):
    
    def __init__(self,master : tk.Tk ,heig : int,wid : int,json_path : str):
        super().__init__(master,height=heig,width=wid)
        self.pack()
        self.search = self.entry_frame()
        self.table = self.tree_frame()
        self.countries = Countries(json_path)
        self.images = {}
        self.current_items = set()
        self.put_all_items()

    def entry_frame(self):
        search_ent_var = tk.StringVar()
        entryFrame = tk.Frame(self)
        self.update()
        entryFrame.place(x=10,y=10,width=self.winfo_width(),height=self.winfo_height())

        label = tk.Label(entryFrame, text= "Busca por nombre de la bandera")
        label.grid(row=0,column=0, padx=5,pady=5)
        
        search_ent = tk.Entry(entryFrame,textvariable=search_ent_var)
        search_ent.grid(row=0,column=1,padx=5)

        search_button = tk.Button(entryFrame,text="Search",command=self.search_function)
        search_button.grid(row=0,column=2,padx=20)
        
        used_button = tk.Button(entryFrame,text="Put as used", command=self.put_to_used)
        used_button.grid(row=0,column=3,padx=20)

        return search_ent_var

    def tree_frame(self):
        treeFrame = tk.Frame(self)
        treeFrame.place(x=10,y=50,width=700,height=700)

        columns_names = ('flags','used','population')
        table = ttk.Treeview(treeFrame,columns=columns_names)
        table.column('#0', width=25, minwidth=25, anchor='center')
        table.column('flags',width=200,minwidth=200)
        table.column('used',width=25,minwidth=25,anchor='center')
        table.column('population',width=100,minwidth=100)

        table.heading('#0', text='Flag')
        table.heading('flags',text='Name')
        table.heading('used',text='Used')
        table.heading('population',text='Population')

        table.pack(fill=tk.BOTH,expand=True)

        return table
    
    def search_function(self,*args):
        search = self.search.get()
        results = self.countries.fuzzy_search(search)

        to_delete = self.current_items.difference(results)
        to_add = results.difference(self.current_items)
        self.current_items = results

        aux = {self.table.set(child,'flags').lower():child for child in self.table.get_children()}
        indexes_to_delete = [aux[name] for name in to_delete]
        
        for idx in indexes_to_delete:
            self.table.delete(idx)
        for name in to_add:
            country = self.countries.get(name=name)
            self.table.insert('',0,image=self.images[name],values=(name.title(),country.used,country.population))
        self.sort_heading('flags',False)
       
    def sort_heading(self,col : str,reverse : bool):
        data = [(self.table.set(child,'flags'),child) for child in self.table.get_children()]
        data.sort(reverse=reverse)
        
        for index, (val,child) in enumerate(data):
            self.table.move(child,'',index)

        self.table.heading(col,command=lambda:self.sort_heading(col,not reverse))

    def put_to_used(self):
        index = self.table.selection()[0]
        name = self.table.item(index)['values'][0]
        
        self.countries.put_to_used(name)
        self.table.delete(index)
        self.current_items.remove(name.lower())
        self.search_function()
        
    def put_all_items(self):
        flags_names = self.countries.get_names()
        for name in flags_names:
            country = self.countries.get(name=name)
            path = country.img
            with Image.open(path) as img_flag:
                self.images[name] = ImageTk.PhotoImage(img_flag.resize((50,25)))
            self.table.insert('',index=tk.END,image=self.images[name],values=(name.title(),country.used,country.population))
            self.current_items.add(name)